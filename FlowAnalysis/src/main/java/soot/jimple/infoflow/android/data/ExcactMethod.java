package soot.jimple.infoflow.android.data;

import soot.SootMethod;
import soot.jimple.infoflow.data.SootMethodAndClass;

import java.util.List;
import java.util.Set;

public class ExcactMethod extends AndroidMethod {

    private Set<StmtLocation> locations;

    public ExcactMethod(String methodName, String returnType, String className, Set<StmtLocation> locations) {
        super(methodName, returnType, className);
        this.locations = locations;
    }

    public ExcactMethod(String methodName, List<String> parameters, String returnType, String className, Set<StmtLocation> locations) {
        super(methodName, parameters, returnType, className);
        this.locations = locations;
    }

    public ExcactMethod(String methodName, String returnType, String className) {
        super(methodName, returnType, className);
    }

    public ExcactMethod(String methodName, List<String> parameters, String returnType, String className) {
        super(methodName, parameters, returnType, className);
    }

    public ExcactMethod(SootMethod sm) {
        super(sm);
    }

    public ExcactMethod(SootMethodAndClass methodAndClass) {
        super(methodAndClass);
    }

    public Set<StmtLocation> getLocations() {
        return locations;
    }

    public void setLocations(Set<StmtLocation> locations) {
        this.locations = locations;
    }
}
