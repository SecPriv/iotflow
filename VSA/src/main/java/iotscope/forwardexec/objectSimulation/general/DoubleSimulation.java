package iotscope.forwardexec.objectSimulation.general;

import iotscope.forwardexec.objectSimulation.SimulationObjects;
import iotscope.forwardexec.objectSimulation.SimulationUtil;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import soot.DoubleType;
import soot.Type;
import soot.Value;
import soot.jimple.*;

import java.util.HashMap;
import java.util.HashSet;

public class DoubleSimulation implements SimulationObjects {

    private static final Logger LOGGER = LoggerFactory.getLogger(DoubleSimulation.class);


    public DoubleSimulation() {
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
        if (rightop instanceof DoubleConstant) {
            HashSet<Double> result = new HashSet<>();
            result.add(((DoubleConstant) rightop).value);
            return result;
        }
        return null;
    }

    @Override
    public HashSet<?> handleAssignNewArrayExpr(AssignStmt stmt, Value rightop, HashMap<Value, HashSet<?>> currentValues) {
        NewArrayExpr newArrayExpr = ((NewArrayExpr) rightop);
        if (newArrayExpr.getBaseType().toString().equals("java.lang.Double") || newArrayExpr.getBaseType() instanceof DoubleType) {
            return SimulationUtil.initArray(0d, newArrayExpr, currentValues);
        }
        return null;
    }


    @Override
    public HashSet<?> handleAssignArithmeticExpr(AssignStmt stmt, Value rightop, HashMap<Value, HashSet<?>> currentValues) {
        //Save cast because it is already checked in the simulation engine if it is a float binop expr
        Value op1 = ((BinopExpr) rightop).getOp1();
        Value op2 = ((BinopExpr) rightop).getOp2();
        Type type = ((BinopExpr) rightop).getOp1().getType();

        if (!(type instanceof DoubleType)) {
            return null;
        }
        HashSet<Double> var1 = SimulationUtil.getDoubleContent(op1, currentValues);
        HashSet<Double> var2 = SimulationUtil.getDoubleContent(op2, currentValues);

        HashSet<Double> result = new HashSet<>();
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
        }


        return result;
    }


}
