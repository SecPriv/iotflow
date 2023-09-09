package iotscope.graph;

import org.json.JSONObject;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

import java.util.HashSet;
import java.util.List;

/**
 * Data dependence Graph
 * <p>
 * If  there  are  any  variables  that contribute to the computation of v0,
 * we add them to our data dependence  graph  (DDG)  and  meanwhile  push  the  involved instructions
 * and  variables  into  a  string  computation  stack
 */
public class DataDependenceGraph {
    private static final Logger LOGGER = LoggerFactory.getLogger(DataDependenceGraph.class);

    private final HashSet<IDataDependenceGraphNode> nodes = new HashSet<>();

    public void addNode(IDataDependenceGraphNode node) {
        nodes.add(node);
    }

    public HashSet<IDataDependenceGraphNode> getNodes() {
        return nodes;
    }

    public void solve(List<ValuePoint> valuePoints) {
        for (ValuePoint valuePoint : valuePoints) {
            this.addNode(valuePoint);
        }

        while (true) {
            initAllIfNeed();
            IDataDependenceGraphNode tnode = getNextSolvableNode();

            if (hasSolvedAllTarget(valuePoints)) {
                LOGGER.info("[DONE]: Solved All Value Points!");
                return;
            }

            if (tnode == null) {
                LOGGER.info("[DONE]: No Solvable Node Left!");
                if (partiallySolvableNodesLeft()) {
                    continue;
                } else {
                    LOGGER.info("[DONE]: No PartiallySolvable Node Left!");
                    return;
                }
            }
            tnode.solve();

        }
    }

    /**
     * Init nodes -> create Backward Contexts
     */
    private void initAllIfNeed() {
        while (true) {
            IDataDependenceGraphNode whoNeedInit = null;
            for (IDataDependenceGraphNode tmp : this.nodes) {
                if (!tmp.inited()) {
                    whoNeedInit = tmp;
                    break;
                }
            }
            if (whoNeedInit == null) {
                return;
            }
            whoNeedInit.initIfHavenot();
        }
    }

    private IDataDependenceGraphNode getNextSolvableNode() {
        for (IDataDependenceGraphNode tmp : this.nodes) {
            if (tmp.getUnsovledDependentsCount() == 0 && !tmp.hasSolved()) {
                return tmp;
            }
        }
        return null;
    }

    /**
     * Can a node be partially solved
     *
     * @return true in case there is such node
     */
    private boolean partiallySolvableNodesLeft() {
        for (IDataDependenceGraphNode tmp : this.nodes) {
            //added not solved check otherwise some results are added twice
            if (!tmp.hasSolved() && tmp.canBePartiallySolve()) {
                return true;
            }
        }
        return false;
    }

    /**
     * check if all value points have been solved
     *
     * @param valuePoints to check
     * @return true in case all are solved
     */
    private boolean hasSolvedAllTarget(List<ValuePoint> valuePoints) {
        for (ValuePoint vp : valuePoints) {
            if (!vp.hasSolved())
                return false;
        }
        return true;
    }

    public JSONObject toJson() {
        JSONObject result = new JSONObject();
        JSONObject jnodes = new JSONObject();
        JSONObject jedges = new JSONObject();
        for (IDataDependenceGraphNode node : nodes) {
            jnodes.put(node.hashCode() + "", node.getClass().getSimpleName());
            for (IDataDependenceGraphNode subn : node.getDependents()) {
                jedges.append(node.hashCode() + "", subn.hashCode() + "");
            }
        }
        result.put("nodes", jnodes);
        result.put("edges", jedges);
        return result;
    }
}
