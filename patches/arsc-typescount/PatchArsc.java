import org.objectweb.asm.ClassReader;
import org.objectweb.asm.ClassWriter;
import org.objectweb.asm.Opcodes;
import org.objectweb.asm.tree.*;

import java.nio.file.Files;
import java.nio.file.Path;

/**
 * Removes the "File format violation, res1 was not zero" check from
 * ARSCFileParser.readTypeSpecTable. Since Android 13, ResTable_typeSpec.res1 is
 * used as "typesCount" and is non-zero, which makes the old parser throw.
 * Only this one check is removed; every other check is left untouched.
 *
 * Usage: java -cp <asm on classpath>:. PatchArsc <in.class> <out.class>
 */
public class PatchArsc {
    static final String MSG = "File format violation, res1 was not zero";

    // Skip labels, line numbers and frames (pseudo-instructions have opcode -1)
    static AbstractInsnNode prev(AbstractInsnNode n) { do { n = n.getPrevious(); } while (n.getOpcode() < 0); return n; }
    static AbstractInsnNode next(AbstractInsnNode n) { do { n = n.getNext(); } while (n.getOpcode() < 0); return n; }

    public static void main(String[] args) throws Exception {
        ClassNode cn = new ClassNode();
        new ClassReader(Files.readAllBytes(Path.of(args[0]))).accept(cn, 0);
        int patched = 0;
        for (MethodNode m : cn.methods) {
            if (!m.name.equals("readTypeSpecTable")) continue;
            for (AbstractInsnNode n : m.instructions.toArray()) {
                if (!(n instanceof LdcInsnNode) || !MSG.equals(((LdcInsnNode) n).cst)) continue;
                // Expected: getfield res1; ifeq L; new RuntimeException; dup; ldc MSG; invokespecial; athrow; L:
                AbstractInsnNode dup = prev(n), neu = prev(dup), jmp = prev(neu);
                AbstractInsnNode inv = next(n), thr = next(inv);
                if (jmp.getOpcode() != Opcodes.IFEQ || neu.getOpcode() != Opcodes.NEW || dup.getOpcode() != Opcodes.DUP
                        || inv.getOpcode() != Opcodes.INVOKESPECIAL || thr.getOpcode() != Opcodes.ATHROW
                        || prev(jmp).getOpcode() != Opcodes.GETFIELD
                        || !((FieldInsnNode) prev(jmp)).name.equals("res1"))
                    throw new IllegalStateException("Unexpected bytecode around the check; not patching");
                // Keep the field read (value stays stored), drop the value instead of branching, remove the throw.
                m.instructions.set(jmp, new InsnNode(Opcodes.POP));
                for (AbstractInsnNode x : new AbstractInsnNode[]{neu, dup, n, inv, thr}) m.instructions.remove(x);
                patched++;
            }
        }
        if (patched != 1) throw new IllegalStateException("Expected exactly 1 check, found " + patched);
        ClassWriter cw = new ClassWriter(ClassWriter.COMPUTE_MAXS);
        cn.accept(cw);
        Files.write(Path.of(args[1]), cw.toByteArray());
        System.out.println("patched " + args[0] + " -> " + args[1]);
    }
}
