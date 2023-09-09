package soot.jimple.infoflow.android.data;

public class StmtLocation {
    private int lineNumber;
    private String parentMethod;

    public StmtLocation(int lineNumber, String parentMethod) {
        this.lineNumber = lineNumber;
        this.parentMethod = parentMethod;
    }

    public int getLineNumber() {
        return lineNumber;
    }

    public void setLineNumber(int lineNumber) {
        this.lineNumber = lineNumber;
    }

    public String getParentMethod() {
        return parentMethod;
    }

    public void setParentMethod(String parentMethod) {
        this.parentMethod = parentMethod;
    }

    @Override
    public boolean equals(Object o) {
        if (this == o) return true;
        if (o == null || getClass() != o.getClass()) return false;

        StmtLocation that = (StmtLocation) o;

        if (lineNumber != that.lineNumber) return false;
        return parentMethod != null ? parentMethod.equals(that.parentMethod) : that.parentMethod == null;
    }

    @Override
    public int hashCode() {
        int result = lineNumber;
        result = 31 * result + (parentMethod != null ? parentMethod.hashCode() : 0);
        return result;
    }

    @Override
    public String toString() {
        return "StmtLocation{" +
                "lineNumber=" + lineNumber +
                ", parentMethod='" + parentMethod + '\'' +
                '}';
    }
}
