package iotscope.forwardexec.objectSimulation.general;

import iotscope.forwardexec.objectSimulation.SimulationObjects;
import iotscope.forwardexec.objectSimulation.SimulationUtil;
import iotscope.main.ApkContext;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import soot.IntType;
import soot.Type;
import soot.Value;
import soot.jimple.*;

import java.util.HashMap;
import java.util.HashSet;

import static iotscope.forwardexec.objectSimulation.SimulationUtil.getIntContent;
import static iotscope.forwardexec.objectSimulation.SimulationUtil.getStringContent;

public class IntegerSimulation implements SimulationObjects {

    private static final Logger LOGGER = LoggerFactory.getLogger(IntegerSimulation.class);



    public IntegerSimulation() {
    }


    @Override
    public HashSet<?> handleInvokeStmt(InvokeStmt stmt, String signature, InvokeExpr expr, HashMap<Value, HashSet<?>> currentValues) {
        return null;
    }

    @Override
    public HashSet<?> handleAssignInvokeExpression(AssignStmt stmt, String signature, InvokeExpr expr, HashMap<Value, HashSet<?>> currentValues) {
        if (signature.equals("<android.content.res.Resources: int getIdentifier(java.lang.String,java.lang.String,java.lang.String)>")) {
            Value leftop = stmt.getLeftOp();
            currentValues.remove(leftop);
            HashSet<Integer> result = new HashSet<>();
            for (String p1 : getStringContent(expr.getArg(0), currentValues)) {
                for (String p2 : getStringContent(expr.getArg(1), currentValues)) {
                    result.add(ApkContext.getInstance().getIdentifier(p1, p2));

                }
            }
            return result;
        } else if (signature.equals("<java.lang.Integer: java.lang.Integer valueOf(int)>")){
            return getIntContent(expr.getArg(0), currentValues);
        }
        return null;
    }

    @Override
    public HashSet<?> handleAssignNewExpression(AssignStmt stmt, Value rightop, HashMap<Value, HashSet<?>> currentValues) {
        return null;
    }

    @Override
    public HashSet<?> handleAssignConstant(AssignStmt stmt, Value rightop, Value leftOp, HashMap<Value, HashSet<?>> currentValues) {
        if (rightop instanceof IntConstant) {
            HashSet<Integer> result = new HashSet<>();
            result.add(((IntConstant) rightop).value);
            return result;
        }
        return null;
    }

    @Override
    public HashSet<?> handleAssignNewArrayExpr(AssignStmt stmt, Value rightop, HashMap<Value, HashSet<?>> currentValues) {
        NewArrayExpr newArrayExpr = ((NewArrayExpr) rightop);
        if (newArrayExpr.getBaseType().toString().equals("java.lang.Integer") || newArrayExpr.getBaseType() instanceof IntType) {
            return SimulationUtil.initArray(0, newArrayExpr, currentValues);
        }
        return null;
    }


    @Override
    public HashSet<?> handleAssignArithmeticExpr(AssignStmt stmt, Value rightop, HashMap<Value, HashSet<?>> currentValues) {
        //Save cast because it is already checked in the simulation engine if it is a float binop expr
        Value op1 = ((BinopExpr) rightop).getOp1();
        Value op2 = ((BinopExpr) rightop).getOp2();
        Type type = ((BinopExpr) rightop).getOp1().getType();

        if (!(type instanceof IntType)) {
            return null;
        }
        HashSet<Integer> var1 = SimulationUtil.getIntContent(op1, currentValues);
        HashSet<Integer> var2 = SimulationUtil.getIntContent(op2, currentValues);

        HashSet<Integer> result = new HashSet<>();
        if (rightop instanceof AddExpr) {
            var1.forEach(
                    v1 -> {
                        var2.forEach(v2 -> {
                            if (result.size() < 100) {
                                result.add(v1 + v2);
                            }
                        });
                    }
            );

        } else if (rightop instanceof DivExpr) {
            var1.forEach(
                    v1 -> {
                        var2.forEach(v2 -> {
                            if (result.size() < 100) {
                                if (v2 != 0) {
                                    result.add(v1 / v2);
                                } else {
                                    result.add(v1);
                                }
                            }
                        });
                    }
            );
        } else if (rightop instanceof MulExpr) {
            var1.forEach(
                    v1 -> {
                        var2.forEach(v2 -> {
                            if (result.size() < 100) {
                                result.add(v1 * v2);
                            }
                        });
                    }
            );
        } else if (rightop instanceof RemExpr) {
            var1.forEach(
                    v1 -> {
                        var2.forEach(v2 -> {
                            if (result.size() < 100) {
                                if (v2 != 0) {
                                    result.add(v1 % v2);
                                } else {
                                    result.add(v1);
                                }
                            }
                        });
                    }
            );
        } else if (rightop instanceof SubExpr) {
            var1.forEach(
                    v1 -> {
                        var2.forEach(v2 -> {
                            if (result.size() < 100) {
                                result.add(v1 - v2);
                            }
                        });
                    }
            );
        }else if (rightop instanceof AndExpr) {
            var1.forEach(
                    v1 -> {
                        var2.forEach(v2 -> {
                            if (result.size() < 100) {
                                result.add((v1 & v2));
                            }
                        });
                    }
            );
        } else if (rightop instanceof OrExpr) {
            var1.forEach(
                    v1 -> {
                        var2.forEach(v2 -> {
                            if (result.size() < 100) {
                                result.add((v1 | v2));
                            }
                        });
                    }
            );
        } else if (rightop instanceof ShlExpr) {
            var1.forEach(
                    v1 -> {
                        var2.forEach(v2 -> {
                            if (result.size() < 100) {
                                result.add((v1 << v2));
                            }
                        });
                    }
            );
        } else if (rightop instanceof ShrExpr) {
            var1.forEach(
                    v1 -> {
                        var2.forEach(v2 -> {
                            if (result.size() < 100) {
                                result.add((v1 >> v2));
                            }
                        });
                    }
            );
        } else if (rightop instanceof UshrExpr) {
            var1.forEach(
                    v1 -> {
                        var2.forEach(v2 -> {
                            if (result.size() < 100) {
                                result.add((v1 >>> v2));
                            }
                        });
                    }
            );
        } else if (rightop instanceof XorExpr) {
            var1.forEach(
                    v1 -> {
                        var2.forEach(v2 -> {
                            if (result.size() < 100) {
                                result.add((v1 ^ v2));
                            }
                        });
                    }
            );
        }


        return result;
    }


}
