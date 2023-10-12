package iotscope.graph;

import iotscope.base.StmtPoint;
import iotscope.utility.ReflectionHelper;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import soot.SootField;
import soot.tagkit.*;

import java.util.*;

public class HeapObject implements IDataDependenciesGraphNode {

    private static final Logger LOGGER = LoggerFactory.getLogger(HeapObject.class);

    private final DataDependenciesGraph dataGraph;

    private final SootField sootField;
    private boolean inited = false;
    private boolean solved = false;

    //Value point where the heap object is set
    private ArrayList<ValuePoint> valuePoints;
    private final HashSet<ValuePoint> solvedValuePoints = new HashSet<>();

    private final Map<Integer, Set<Object>> result = new HashMap<>();

    private HeapObject(DataDependenciesGraph dataGraph, SootField sootField) {
        this.dataGraph = dataGraph;
        this.sootField = sootField;
    }

    private final static HashMap<String, HeapObject> HEAP_OBJECT_HASH_MAP = new HashMap<>();

    public static HeapObject getInstance(DataDependenciesGraph dataGraph, SootField sootField) {
        if (sootField == null) {
            return null;
        }
        String str = sootField.toString();
        if (!HEAP_OBJECT_HASH_MAP.containsKey(str)) {
            HEAP_OBJECT_HASH_MAP.put(str, new HeapObject(dataGraph, sootField));
        }
        return HEAP_OBJECT_HASH_MAP.get(str);
    }


    @Override
    public Set<IDataDependenciesGraphNode> getDependents() {
        return new HashSet<>(valuePoints);

    }

    @Override
    public int getUnsovledDependentsCount() {
        int count = 0;
        for (IDataDependenciesGraphNode vp : getDependents()) {
            if (!vp.hasSolved()) {
                count++;
            }
        }
        return count;
    }

    @Override
    public boolean hasSolved() {
        return solved;
    }

    @Override
    public void solve() {
        this.solved = true;
        LOGGER.debug("[HEAP SOLVE]" + this.sootField);
        LOGGER.debug("[SOLVING ME]" + this.hashCode());

        for (ValuePoint valuePoint : this.valuePoints) {
            Map<Integer, Set<Object>> vpResult = valuePoint.getResult();
            // -1 == Heap Object?
            if (vpResult.containsKey(-1)) {
                Set<Object> toAdd = result.getOrDefault(-1, new HashSet<>());
                vpResult.get(-1).forEach(x -> {
                    try {
                            toAdd.add(x);
                    } catch (Throwable e) {
                        LOGGER.debug("Could not add result object {}", e.getMessage());
                    }
                });
                result.put(-1, toAdd);
            }
        }
        addDefault();
    }

    private void addDefault() {
        if (!result.containsKey(-1)) {
            Set<Object> toAdd = new HashSet<>();
            toAdd.add(this.sootField.getName());
            result.put(-1, toAdd);
        }
    }

    @Override
    public boolean canBePartiallySolve() {
        boolean canBePartiallySolved = false;
        for (ValuePoint valuePoint : this.valuePoints) {
            if (!this.solvedValuePoints.contains(valuePoint) && valuePoint.hasSolved()) {
                this.solvedValuePoints.add(valuePoint);
                canBePartiallySolved = true;
                Map<Integer, Set<Object>> res = valuePoint.getResult();
                if (res.containsKey(-1)) {
                    Set<Object> toAdd = result.getOrDefault(-1, new HashSet<>());
                    for (Object obj : res.get(-1)) {
                            try {
                                toAdd.add(obj);
                            }catch (ClassCastException e) {
                                //we can't do anything
                            }
                    }
                    result.put(-1, toAdd);
                }
            }

        }
        if (canBePartiallySolved) {
            solved = true;
            addDefault();
        }
        return canBePartiallySolved;
    }

    private void addValueToResult(Object valueToAdd) {
        try {
            Set<Object> toAdd = result.getOrDefault(-1, new HashSet<>());
                toAdd.add(valueToAdd);
                result.put(-1, toAdd);
        } catch (Throwable e) {
            LOGGER.error("could not add reflection object " );
        }
    }

    @Override
    public void initIfHaveNot() {
        this.valuePoints = new ArrayList<>();
        if (this.sootField.getDeclaringClass().isEnum()) {
            Object toAdd = ReflectionHelper.getEnumObject(sootField, sootField.getDeclaringClass().getName());
            if (toAdd == null) {
                toAdd = sootField.getName();
            }
            addValueToResult(toAdd);
            inited = true;
            return;
        } else {
            Object object = ReflectionHelper.getDefaultValue(sootField, sootField.getDeclaringClass().getName());
            if (object != null) {
                addValueToResult(object);
            } else {
                Optional<Tag> constantTag = this.sootField.getTags().stream().filter(t -> t instanceof ConstantValueTag).findFirst();
                if (constantTag.isPresent()) {
                    Tag tag = constantTag.get();
                    LOGGER.info("Init SootField {} with Value {}", this.sootField, tag);
                    if (tag instanceof StringConstantValueTag) {
                        addValueToResult(((StringConstantValueTag) tag).getStringValue());
                    } else if (tag instanceof IntegerConstantValueTag) {
                        addValueToResult(((IntegerConstantValueTag) tag).getIntValue());
                    } else if (tag instanceof FloatConstantValueTag) {
                        addValueToResult(((FloatConstantValueTag) tag).getFloatValue());
                    } else if (tag instanceof LongConstantValueTag) {
                        addValueToResult(((LongConstantValueTag) tag).getLongValue());
                    } else if (tag instanceof DoubleConstantValueTag) {
                        addValueToResult(((DoubleConstantValueTag) tag).getDoubleValue());
                    }
                }
            }
        }


        List<StmtPoint> stmtPoints = StmtPoint.findSetter(this.sootField);
        for (StmtPoint stmtPoint : stmtPoints) {
            ValuePoint tmp = new ValuePoint(dataGraph, stmtPoint.getMethodLocation(), stmtPoint.getBlockLocation(), stmtPoint.getInstructionLocation(), Collections.singletonList(-1));
            valuePoints.add(tmp);
            tmp.setCreatingHeapObject(this);
        }


        LOGGER.debug("[HEAP INIT]" + sootField + " " + StmtPoint.findSetter(sootField).size());
        inited = true;

    }

    @Override
    public boolean inited() {
        return inited;
    }

    @Override
    public Set<IDataDependenciesGraphNode> getDirectAndIndirectDependents
            (Set<IDataDependenciesGraphNode> nodesToGetDependencies) {
        for (IDataDependenciesGraphNode i : this.getDependents()) {
            if (!nodesToGetDependencies.contains(i)) {
                nodesToGetDependencies.add(i);
                i.getDirectAndIndirectDependents(nodesToGetDependencies);
            }
        }
        return nodesToGetDependencies;
    }

    @Override
    public Map<Integer, Set<Object>> getResult() {
        return result;
    }

    @Override
    public int hashCode() {
        final int prime = 31;
        int result = 1;
        result = prime * result + ((sootField == null) ? 0 : sootField.hashCode());
        return result;
    }

    @Override
    public boolean equals(Object obj) {
        if (this == obj)
            return true;
        if (obj == null)
            return false;
        if (getClass() != obj.getClass())
            return false;
        HeapObject other = (HeapObject) obj;
        if (sootField == null) {
            return other.sootField == null;
        } else {
            return sootField.equals(other.sootField);
        }
    }

    @Override
    public String toString() {
        if (!inited)
            return super.toString();
        StringBuilder sb = new StringBuilder();
        sb.append("===========================");
        sb.append(this.hashCode());
        sb.append("===========================\n");
        sb.append("Field: ").append(sootField).append("\n");
        sb.append("Solved: ").append(hasSolved()).append("\n");
        sb.append("Depend: ");
        for (IDataDependenciesGraphNode var : this.getDependents()) {
            sb.append(var.hashCode());
            sb.append(", ");
        }
        sb.append("\n");
        sb.append("ValueSet: \n");
        Map<Integer, Set<Object>> resultMap = result;
        sb.append("  ");
        for (int i : resultMap.keySet()) {
            sb.append(" |").append(i).append(":");
            for (Object str : resultMap.get(i)) {
                sb.append(str == null ? "" : str.toString()).append(",");
            }
        }
        sb.append("\n");


        return sb.toString();
    }


}
