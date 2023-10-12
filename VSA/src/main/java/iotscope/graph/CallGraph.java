package iotscope.graph;

import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import soot.*;
import soot.jimple.FieldRef;
import soot.jimple.Stmt;
import soot.util.Chain;

import java.util.ArrayList;
import java.util.HashSet;
import java.util.Hashtable;
import java.util.List;

/**
 * Creates the CallGraph of the application under analysis
 */
public class CallGraph {

    private static final Logger LOGGER = LoggerFactory.getLogger(CallGraph.class);

    //Key the string of the soot method
    // map with the sootMethod name and the CallGraphNode of the sootMethod
    private static final Hashtable<String, CallGraphNode> nodes = new Hashtable<>();

    // Maps Soot Field String to the soot Methods it is referenced
    private static final Hashtable<String, HashSet<SootMethod>> fieldSetters = new Hashtable<>();

    public static void init() {
        long startTime = System.currentTimeMillis();

        Chain<SootClass> classes = Scene.v().getClasses();
        try {
            //init the nodes map
            for (SootClass sootClass : classes) {
                List<SootMethod> methods = new ArrayList<>(sootClass.getMethods());
                for (SootMethod sootMethod : methods) {
                    CallGraphNode tmpNode = new CallGraphNode(sootMethod);
                    nodes.put(sootMethod.toString(), tmpNode);
                    if (sootMethod.isConcrete()) {
                        try {
                            sootMethod.retrieveActiveBody();
                        } catch (Exception e) {
                            LOGGER.error("Could not retrieved the active body of {} because {}", sootMethod, e.getLocalizedMessage());
                        }
                    }
                }
            }

            LOGGER.debug("[CG time]: " + (System.currentTimeMillis() - startTime));
            for (SootClass sootClass : classes) {
                for (SootMethod sootMethod : clone(sootClass.getMethods())) {
                    if (!sootMethod.isConcrete())
                        continue;


                    Body body = null;
                    try {
                        body = sootMethod.retrieveActiveBody();
                    } catch (Exception e) {
                        LOGGER.error("Could not retrieved the active body of {} because {}", sootMethod, e.getLocalizedMessage());
                    }
                    if (body == null)
                        continue;
                    for (Unit unit : body.getUnits()) {
                        if (unit instanceof Stmt) {
                            if (((Stmt) unit).containsInvokeExpr()) {
                                try {
                                    addCall(sootMethod, ((Stmt) unit).getInvokeExpr().getMethod());
                                } catch (Exception e) {
                                    LOGGER.error(e.getMessage());
                                }
                            }
                            for (ValueBox valueBox : unit.getDefBoxes()) {
                                Value temporaryValue = valueBox.getValue();
                                if (temporaryValue instanceof FieldRef) {
                                    FieldRef fieldRef = (FieldRef) temporaryValue;
                                    if (fieldRef.getField() == null || fieldRef.getField().getDeclaringClass() == null) {
                                        continue;
                                    }
                                    if (fieldRef.getField().getDeclaringClass().isApplicationClass()) {
                                        String str = fieldRef.getField().toString();
                                        if (!fieldSetters.containsKey(str)) {
                                            fieldSetters.put(str, new HashSet<>());
                                        }
                                        fieldSetters.get(str).add(sootMethod);
                                    }
                                }
                            }
                        }
                    }
                }
            }
        } catch (Throwable e) {
            LOGGER.error("error init call graph");
        }

        LOGGER.info("[CG time]:" + (System.currentTimeMillis() - startTime));
    }

    /**
     * Add to the call graph nodes the information about the callee and caller
     *
     * @param from add to the from node the call information
     * @param to   add to the to node the caller information
     */
    private static void addCall(SootMethod from, SootMethod to) {
        CallGraphNode fromNode, toNode;
        fromNode = getNode(from);
        toNode = getNode(to);
        if (fromNode == null || toNode == null) {
            LOGGER.debug("Can't add call because from or to node is null");
            return;
        }

        fromNode.addCallTo(toNode);
        toNode.addCallBy(fromNode);

    }

    /**
     * get CallGraphNode from Soot Method
     *
     * @param from to get CallGraphNode from
     * @return the corresponding node
     */
    public static CallGraphNode getNode(SootMethod from) {
        return getNode(from.toString());
    }

    /**
     * get CallGraphNode from Soot Method
     *
     * @param from SootMethodString to get the CallGraphNode from
     * @return the corresponding node
     */
    public static CallGraphNode getNode(String from) {
        return nodes.get(from);
    }

    public static HashSet<SootMethod> getSetter(SootField sootField) {
        return fieldSetters.get(sootField.toString());
    }


    public static <T> List<T> clone(List<T> ls) {
        return new ArrayList<T>(ls);
    }
}
