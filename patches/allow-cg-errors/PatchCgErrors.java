import org.objectweb.asm.ClassReader;
import org.objectweb.asm.ClassWriter;
import org.objectweb.asm.Opcodes;
import org.objectweb.asm.tree.*;

import java.nio.file.Files;
import java.nio.file.Path;

/**
 * Makes Soot's Spark call-graph builder skip methods it cannot process instead of aborting.
 *
 * In soot.jimple.spark.solver.OnFlyCallGraph.processReachables(), Soot wraps the per-method PAG
 * construction in try/catch and rethrows unless Options.v().allow_cg_errors() is true. FlowDroid
 * does not expose that option. This patch replaces the call to allow_cg_errors() with the constant
 * true, so the error is logged ("An error occurred while processing <method> in callgraph") and the
 * analysis continues without that method's pointer information.
 *
 * Usage: java -cp <asm on classpath>:. PatchCgErrors <in.class> <out.class>
 */
public class PatchCgErrors {
    public static void main(String[] args) throws Exception {
        ClassNode cn = new ClassNode();
        new ClassReader(Files.readAllBytes(Path.of(args[0]))).accept(cn, 0);
        int patched = 0;
        for (MethodNode m : cn.methods) {
            if (!m.name.equals("processReachables")) continue;
            for (AbstractInsnNode insn : m.instructions.toArray()) {
                if (insn instanceof MethodInsnNode) {
                    MethodInsnNode mi = (MethodInsnNode) insn;
                    if (mi.getOpcode() == Opcodes.INVOKEVIRTUAL && mi.owner.equals("soot/options/Options")
                            && mi.name.equals("allow_cg_errors") && mi.desc.equals("()Z")) {
                        // Options.v() is still on the stack: drop it and push true instead
                        InsnList repl = new InsnList();
                        repl.add(new InsnNode(Opcodes.POP));
                        repl.add(new InsnNode(Opcodes.ICONST_1));
                        m.instructions.insert(mi, repl);
                        m.instructions.remove(mi);
                        patched++;
                    }
                }
            }
        }
        if (patched != 1) throw new IllegalStateException("expected 1 call to allow_cg_errors(), found " + patched);
        ClassWriter cw = new ClassWriter(ClassWriter.COMPUTE_MAXS);
        cn.accept(cw);
        Files.write(Path.of(args[1]), cw.toByteArray());
        System.out.println("patched " + args[0] + " -> " + args[1]);
    }
}
