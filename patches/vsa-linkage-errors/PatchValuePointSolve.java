import org.objectweb.asm.ClassReader;
import org.objectweb.asm.ClassWriter;
import org.objectweb.asm.Opcodes;
import org.objectweb.asm.tree.*;

import java.io.File;
import java.net.URL;
import java.net.URLClassLoader;
import java.nio.file.Files;
import java.nio.file.Path;

/**
 * IoTScope (VSA): keep going when simulating one backward path hits a LinkageError.
 *
 * In iotscope.graph.ValuePoint.solve(), each backward context is simulated with
 * {@code tmp.simulate(); mergeResult(bc, tmp);}. The simulation loads dex2jar-converted app classes
 * (e.g. via toString() while formatting debug messages); a class that fails Java's verifier throws
 * java.lang.VerifyError, which nothing catches, so the whole analysis of the app ended.
 *
 * The patch wraps these two calls in try/catch(LinkageError) (VerifyError, NoClassDefFoundError,
 * ExceptionInInitializerError, ...). On such an error, the backward context is skipped and the loop
 * continues with the next one. Other errors (e.g. OutOfMemoryError) are not caught.
 *
 * Usage: java -cp <vsa.jar>:. PatchValuePointSolve <vsa.jar> <in.class> <out.class>
 */
public class PatchValuePointSolve {
    public static void main(String[] args) throws Exception {
        ClassNode cn = new ClassNode();
        new ClassReader(Files.readAllBytes(Path.of(args[1]))).accept(cn, 0);
        MethodNode solve = cn.methods.stream()
                .filter(m -> m.name.equals("solve") && m.desc.equals("()V")).findFirst().orElseThrow();

        MethodInsnNode simulate = null, merge = null;
        for (AbstractInsnNode i : solve.instructions.toArray()) {
            if (i instanceof MethodInsnNode) {
                MethodInsnNode mi = (MethodInsnNode) i;
                if (mi.name.equals("simulate") && mi.owner.equals("iotscope/forwardexec/SimulateEngine")) simulate = mi;
                if (mi.name.equals("mergeResult")) merge = mi;
            }
        }
        if (simulate == null || merge == null) throw new IllegalStateException("calls not found");
        // Loop head: the GOTO right after mergeResult jumps back to it
        AbstractInsnNode afterMerge = merge.getNext();
        while (afterMerge.getOpcode() < 0) afterMerge = afterMerge.getNext();
        if (afterMerge.getOpcode() != Opcodes.GOTO) throw new IllegalStateException("unexpected loop shape");
        LabelNode loopHead = ((JumpInsnNode) afterMerge).label;

        // Start of the protected range: the ALOAD of the SimulateEngine local before simulate()
        AbstractInsnNode startInsn = simulate.getPrevious();
        while (startInsn.getOpcode() < 0) startInsn = startInsn.getPrevious();
        LabelNode start = new LabelNode(), end = new LabelNode(), handler = new LabelNode();
        solve.instructions.insertBefore(startInsn, start);
        solve.instructions.insert(merge, end);

        InsnList h = new InsnList();
        h.add(handler);
        h.add(new InsnNode(Opcodes.POP));               // drop the LinkageError, skip this context
        h.add(new JumpInsnNode(Opcodes.GOTO, loopHead));
        solve.instructions.add(h);
        solve.tryCatchBlocks.add(new TryCatchBlockNode(start, end, handler, "java/lang/LinkageError"));

        ClassLoader cl = new URLClassLoader(new URL[]{new File(args[0]).toURI().toURL()},
                PatchValuePointSolve.class.getClassLoader());
        ClassWriter cw = new ClassWriter(ClassWriter.COMPUTE_FRAMES) {
            @Override
            protected ClassLoader getClassLoader() { return cl; }
        };
        cn.accept(cw);
        Files.write(Path.of(args[2]), cw.toByteArray());
        System.out.println("patched " + args[1] + " -> " + args[2]);
    }
}
