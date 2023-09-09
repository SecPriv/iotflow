package iotscope.graph;

import java.util.Map;
import java.util.Set;

/**
 * DataDepenceGraphNode -> Value Point or Heap Objet
 */
public interface IDataDependenceGraphNode {

    /**
     * @return dependent nodes
     */
    Set<IDataDependenceGraphNode> getDependents();

    /**
     * @return the number of not solve dependents node
     */
    int getUnsovledDependentsCount();

    /**
     * @return true if the node is solved
     */
    boolean hasSolved();

    /**
     * solve Value Points with simulation engines
     */
    void solve();

    /**
     * @return if the Node can be partially solved (and tries to solve the value point)
     */
    boolean canBePartiallySolve();

    /**
     * Inits the Node if it has not already been initialized
     */
    void initIfHavenot();

    /**
     * Return true if the node is already inited
     *
     * @return inited
     */
    boolean inited();

    /**
     * @return the results
     */
    Map<Integer, Set<Object>> getResult();

    Set<IDataDependenceGraphNode> getDirectAndIndirectDependents(Set<IDataDependenceGraphNode> ret);
}
