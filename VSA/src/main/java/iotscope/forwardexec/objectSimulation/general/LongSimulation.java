package iotscope.forwardexec.objectSimulation.general;

import iotscope.forwardexec.objectSimulation.SimulationObjects;
import iotscope.forwardexec.objectSimulation.SimulationUtil;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import soot.IntType;
import soot.LongType;
import soot.Type;
import soot.Value;
import soot.jimple.*;

import java.util.HashMap;
import java.util.HashSet;

public class LongSimulation implements SimulationObjects {

    private static final Logger LOGGER = LoggerFactory.getLogger(LongSimulation.class);


    public LongSimulation() {
    }


    @Override
    public HashSet<?> handleInvokeStmt(InvokeStmt stmt, String signature, InvokeExpr expr, HashMap<Value, HashSet<?>> currentValues) {
        return null;
    }

    @Override
    public HashSet<?> handleAssignInvokeExpression(AssignStmt stmt, String signature, InvokeExpr expr, HashMap<Value, HashSet<?>> currentValues) {
        return null;
    }

    @Override
    public HashSet<?> handleAssignNewExpression(AssignStmt stmt, Value rightop, HashMap<Value, HashSet<?>> currentValues) {
        return null;
    }

    @Override
    public HashSet<?> handleAssignConstant(AssignStmt stmt, Value rightop, Value leftOp, HashMap<Value, HashSet<?>> currentValues) {
        if (rightop instanceof LongConstant) {
            HashSet<Long> result = new HashSet<>();
            result.add(((LongConstant) rightop).value);
            return result;
        }
        return null;
    }

    @Override
    public HashSet<?> handleAssignNewArrayExpr(AssignStmt stmt, Value rightop, HashMap<Value, HashSet<?>> currentValues) {
        NewArrayExpr newArrayExpr = ((NewArrayExpr) rightop);
        if (newArrayExpr.getBaseType().toString().equals("java.lang.Long") || newArrayExpr.getBaseType() instanceof LongType) {
            return SimulationUtil.initArray(0L, newArrayExpr, currentValues);
        }
        return null;
    }


    @Override
    public HashSet<?> handleAssignArithmeticExpr(AssignStmt stmt, Value rightop, HashMap<Value, HashSet<?>> currentValues) {
        Value op1 = ((BinopExpr) rightop).getOp1();
        Value op2 = ((BinopExpr) rightop).getOp2();
        Type type = ((BinopExpr) rightop).getOp1().getType();

        if (!(type instanceof IntType)) {
            return null;
        }
        HashSet<Long> var1 = SimulationUtil.getLongContent(op1, currentValues);
        HashSet<Long> var2 = SimulationUtil.getLongContent(op2, currentValues);

        HashSet<Long> result = new HashSet<>();
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
        } else if (rightop instanceof AndExpr) {
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
