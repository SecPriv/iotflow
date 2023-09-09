package soot.jimple.infoflow.android.source;

import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import soot.jimple.infoflow.android.data.AndroidMethod;
import soot.jimple.infoflow.android.data.ExcactMethod;
import soot.jimple.infoflow.android.data.StmtLocation;
import soot.jimple.infoflow.android.data.parsers.PermissionMethodParser;
import soot.jimple.infoflow.data.SootFieldAndClass;
import soot.jimple.infoflow.sourcesSinks.definitions.*;

import java.io.*;
import java.util.*;
import java.util.regex.Matcher;
import java.util.regex.Pattern;

public class SourceSinkListParser implements ISourceSinkDefinitionProvider {

    private final Logger logger = LoggerFactory.getLogger(getClass());

    private Map<String, ExcactMethod> methods = null;
    private Map<String, SootFieldAndClass> fields = null;
    private Set<ISourceSinkDefinition> sourceList = null;
    private Set<ISourceSinkDefinition> sinkList = null;
    private Set<ISourceSinkDefinition> neitherList = null;

    private static final int INITIAL_SET_SIZE = 10000;

    private List<String> data;
    private final String regex = "^<(.+):\\s*(.*)\\s+(.*)\\s*\\((.*)\\)>\\s*->\\s*(_\\w+_)\\s*\\[?(.*)\\]?$";
    // private final String regexNoRet =
    // "^<(.+):\\s(.+)\\s?(.+)\\s*\\((.*)\\)>\\s+(.*?)(\\s+->\\s+(.*))?+$";
    private final String regexNoRet = "^<(.+):\\s*(.+)\\s*\\((.*)\\)>\\s*(.*?)?(\\s+->\\s+(.*))?$";

    private final String fieldRegex = "^<(.+):\\s*(.+)\\s+([a-zA-Z_$][a-zA-Z_$0-9]*)\\s*>\\s*(.*?)(\\s+->\\s+(.*))?$";

    public static SourceSinkListParser fromFile(String fileName) throws IOException {
        SourceSinkListParser pmp = new SourceSinkListParser();
        pmp.readFile(fileName);
        pmp.parse();
        return pmp;
    }

    public static SourceSinkListParser fromStream(InputStream input) throws IOException {
        SourceSinkListParser pmp = new SourceSinkListParser();
        pmp.readReader(new InputStreamReader(input));
        return pmp;
    }

    public static SourceSinkListParser fromStringList(List<String> data) throws IOException {
        SourceSinkListParser pmp = new SourceSinkListParser(data);
        return pmp;
    }

    private SourceSinkListParser() {
    }

    private SourceSinkListParser(List<String> data) {
        this.data = data;
    }

    private void readFile(String fileName) throws IOException {
        FileReader fr = null;
        try {
            fr = new FileReader(fileName);
            readReader(fr);
        } finally {
            if (fr != null)
                fr.close();
        }
    }

    private void readReader(Reader r) throws IOException {
        String line;
        this.data = new ArrayList<String>();
        BufferedReader br = new BufferedReader(r);
        try {
            while ((line = br.readLine()) != null)
                this.data.add(line);
        } finally {
            br.close();
        }

    }

    @Override
    public Set<ISourceSinkDefinition> getSources() {
        if (sourceList == null || sinkList == null)
            parse();
        return this.sourceList;
    }

    @Override
    public Set<ISourceSinkDefinition> getSinks() {
        if (sourceList == null || sinkList == null)
            parse();
        return this.sinkList;
    }

    private void parse() {
        fields = new HashMap<>(INITIAL_SET_SIZE);
        methods = new HashMap<>(INITIAL_SET_SIZE);
        sourceList = new HashSet<>(INITIAL_SET_SIZE);
        sinkList = new HashSet<>(INITIAL_SET_SIZE);
        neitherList = new HashSet<>(INITIAL_SET_SIZE);

        Pattern p = Pattern.compile(regex);
        Pattern pNoRet = Pattern.compile(regexNoRet);
        Pattern fieldPattern = Pattern.compile(fieldRegex);

        for (String line : this.data) {
            if (line.isEmpty() || line.startsWith("%"))
                continue;
            //match field regex
            Matcher fieldMatch = fieldPattern.matcher(line);
            if (fieldMatch.find()) {
                createField(fieldMatch);
            } else {
                //match method regex
                Matcher m = p.matcher(line);
                if (m.find()) {
                    createMethod(m);
                } else {
                    Matcher mNoRet = pNoRet.matcher(line);
                    if (mNoRet.find()) {
                        createMethod(mNoRet);
                    } else
                        logger.warn(String.format("Line does not match: %s", line));
                }
            }
        }

        // Create the source/sink definitions[for method]
        for (AndroidMethod am : methods.values()) {
            MethodSourceSinkDefinition singleMethod = new MethodSourceSinkDefinition(am);

            if (am.getSourceSinkType().isSource())
                sourceList.add(singleMethod);
            if (am.getSourceSinkType().isSink())
                sinkList.add(singleMethod);
            if (am.getSourceSinkType() == SourceSinkType.Neither)
                neitherList.add(singleMethod);
        }

        // Create the source/sink definitions[for field]
        for (SootFieldAndClass sootField : fields.values()) {
            FieldSourceSinkDefinition fieldDefinition = new FieldSourceSinkDefinition(sootField.getSignature());

            if (sootField.getSourceSinkType().isSource())
                sourceList.add(fieldDefinition);
            if (sootField.getSourceSinkType().isSink())
                sinkList.add(fieldDefinition);
            if (sootField.getSourceSinkType() == SourceSinkType.Neither)
                neitherList.add(fieldDefinition);
        }
    }

    private AndroidMethod createMethod(Matcher m) {
        ExcactMethod am = parseMethod(m, true);
        ExcactMethod oldMethod = methods.get(am.getSignature());
        if (oldMethod != null) {
            oldMethod.setSourceSinkType(oldMethod.getSourceSinkType().addType(am.getSourceSinkType()));
            return oldMethod;
        } else {
            methods.put(am.getSignature(), am);
            return am;
        }
    }

    private int getNumber(String numberString) {
        try {
            numberString = numberString.replace("[", "");
            numberString = numberString.replace("]", "");

            return Integer.parseInt(numberString);
        } catch(NumberFormatException e){
            return -1;
        }
    }

    private ExcactMethod parseMethod(Matcher m, boolean hasReturnType) {
        assert (m.group(1) != null && m.group(2) != null && m.group(3) != null && m.group(4) != null);
        ExcactMethod singleMethod;
        int groupIdx = 1;

        // class name
        String className = m.group(groupIdx++).trim();

        String returnType = "";
        if (hasReturnType) {
            // return type
            returnType = m.group(groupIdx++).trim();
        }

        // method name
        String methodName = m.group(groupIdx++).trim();

        // method parameter
        List<String> methodParameters = new ArrayList<String>();
        String params = m.group(groupIdx++).trim();
        if (!params.isEmpty())
            for (String parameter : params.split(","))
                methodParameters.add(parameter.trim());

        // return type
        String classData = "";
        if (m.group(groupIdx) != null) {
            classData = m.group(groupIdx++).replace("->", "").trim();
        }
        // exact Matches
        String locations = "";
        Set<StmtLocation> stmtLocations = new HashSet<>();
        if (m.group(groupIdx) != null) {
            locations = m.group(groupIdx).trim();
        }
        if (!locations.equals("")) {
            String[] allLocations = locations.split("\\|");
            for (String current : allLocations) {
                String[] currentLocation = current.split(";");
                if (currentLocation.length == 2) {
                    String parentMethod = currentLocation[0];
                    int lineNumber = getNumber(currentLocation[1]);
                    stmtLocations.add(new StmtLocation(lineNumber, parentMethod));
                }
            }
        }


        // create method signature
        singleMethod = new ExcactMethod(methodName, methodParameters, returnType, className, stmtLocations);

        if (!classData.isEmpty())
            for (String target : classData.split("\\s")) {
                target = target.trim();

                // Throw away categories
                if (target.contains("|"))
                    target = target.substring(target.indexOf('|'));

                if (!target.isEmpty() && !target.startsWith("|")) {
                    if (target.equals("_SOURCE_"))
                        singleMethod.setSourceSinkType(SourceSinkType.Source);
                    else if (target.equals("_SINK_"))
                        singleMethod.setSourceSinkType(SourceSinkType.Sink);
                    else if (target.equals("_NONE_"))
                        singleMethod.setSourceSinkType(SourceSinkType.Neither);
                    else if (target.equals("_BOTH_"))
                        singleMethod.setSourceSinkType(SourceSinkType.Both);
                    else
                        throw new RuntimeException("error in target definition: " + target);
                }
            }
        return singleMethod;
    }

    @Override
    public Set<ISourceSinkDefinition> getAllMethods() {
        if (sourceList == null || sinkList == null)
            parse();

        Set<ISourceSinkDefinition> sourcesSinks = new HashSet<>(
                sourceList.size() + sinkList.size() + neitherList.size());
        sourcesSinks.addAll(sourceList);
        sourcesSinks.addAll(sinkList);
        sourcesSinks.addAll(neitherList);
        return sourcesSinks;
    }

    private SootFieldAndClass createField(Matcher m) {
        SootFieldAndClass sootField = parseField(m);
        SootFieldAndClass oldField = fields.get(sootField.getSignature());
        if (oldField != null) {
            oldField.setSourceSinkType(oldField.getSourceSinkType().addType(sootField.getSourceSinkType()));
            return oldField;
        } else {
            fields.put(sootField.getSignature(), sootField);
            return sootField;
        }
    }

    private SootFieldAndClass parseField(Matcher m) {
        assert (m.group(1) != null && m.group(2) != null && m.group(3) != null && m.group(4) != null);
        SootFieldAndClass sootFieldAndClass;
        int groupIdx = 1;

        // class name
        String className = m.group(groupIdx++).trim();

        // field type
        String fieldType = m.group(groupIdx++).trim();

        // field name
        String fieldName = m.group(groupIdx++).trim();

        // SourceSinkType
        String sourceSinkTypeString = m.group(groupIdx).replace("->", "").replace("_", "").trim();
        SourceSinkType sourceSinkType = SourceSinkType.fromString(sourceSinkTypeString);

        // create Field signature
        sootFieldAndClass = new SootFieldAndClass(fieldName, className, fieldType, sourceSinkType);

        return sootFieldAndClass;
    }

}

