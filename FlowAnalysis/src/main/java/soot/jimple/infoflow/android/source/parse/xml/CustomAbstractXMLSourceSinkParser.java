package soot.jimple.infoflow.android.source.parse.xml;


import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.xml.sax.Attributes;
import org.xml.sax.SAXException;
import org.xml.sax.helpers.DefaultHandler;
import soot.jimple.infoflow.android.data.AndroidMethod;
import soot.jimple.infoflow.android.data.CategoryDefinition;
import soot.jimple.infoflow.android.data.ExcactMethod;
import soot.jimple.infoflow.android.data.StmtLocation;
import soot.jimple.infoflow.android.source.parsers.xml.AbstractXMLSourceSinkParser;
import soot.jimple.infoflow.android.source.parsers.xml.ResourceUtils;
import soot.jimple.infoflow.android.source.parsers.xml.CustomXMLConstants;
import soot.jimple.infoflow.data.AbstractMethodAndClass;
import soot.jimple.infoflow.river.AdditionalFlowCondition;
import soot.jimple.infoflow.sourcesSinks.definitions.*;

import javax.xml.parsers.ParserConfigurationException;
import javax.xml.parsers.SAXParser;
import javax.xml.parsers.SAXParserFactory;
import java.io.File;
import java.io.FileInputStream;
import java.io.IOException;
import java.io.InputStream;
import java.util.*;

/**
 * Abstract class for all Flowdroid XML parsers. Returns a Set of Methods when
 * calling the function parse. Subclasses may implement parser specifics to
 * different language engines.
 *
 * Modified (AbstractXMLSourceSinkParser) XML parser to allow exact method locations.
 *
 */
public abstract class CustomAbstractXMLSourceSinkParser {
    private final static Logger logger = LoggerFactory.getLogger(CustomAbstractXMLSourceSinkParser.class);

    /**
     * Handler class for the XML parser
     *
     * @author Anna-Katharina Wickert
     * @author Joern Tillmans
     * @author Steven Arzt
     */
    protected class SAXHandler extends DefaultHandler {

        // Holding temporary values for handling with SAX
        protected String methodSignature = null;
        protected String fieldSignature = null;

        protected ISourceSinkCategory category;
        protected boolean isSource, isSink;
        protected List<String> pathElements;
        protected List<String> pathElementTypes;
        protected int paramIndex;
        protected List<String> paramTypes = new ArrayList<String>();
        protected MethodSourceSinkDefinition.CallType callType;

        protected String accessPathParentElement = "";
        protected String description = "";

        protected Set<AccessPathTuple> baseAPs = new HashSet<>();
        protected List<Set<AccessPathTuple>> paramAPs = new ArrayList<>();
        protected Set<AccessPathTuple> returnAPs = new HashSet<>();

        protected AbstractXMLSourceSinkParser.ICategoryFilter categoryFilter = null;

        private Set<String> signaturesOnPath = new HashSet<>();
        private Set<String> classNamesOnPath = new HashSet<>();
        private Set<StmtLocation> stmtLocations = new HashSet<>();

        private Set<String> excludedClassNames = new HashSet<>();
        private Set<SourceSinkCondition> conditions = new HashSet<>();

        public SAXHandler() {
        }

        public SAXHandler(AbstractXMLSourceSinkParser.ICategoryFilter categoryFilter) {
            this.categoryFilter = categoryFilter;
        }

        /**
         * Event Handler for the starting element for SAX. Possible start elements for
         * filling AndroidMethod objects with the new data format: - method: Setting
         * parsingvalues to false or null and get and set the signature and category, -
         * accessPath: To get the information whether the AndroidMethod is a sink or
         * source, - and the other elements doesn't care for creating the AndroidMethod
         * object. At these element we will look, if calling the method getAccessPath
         * (using an new SAX Handler)
         */
        @Override
        public void startElement(String uri, String localName, String qName, Attributes attributes)
                throws SAXException {
            String qNameLower = qName.toLowerCase();
            switch (qNameLower) {
                case CustomXMLConstants.CATEGORY_TAG:
                    handleStarttagCategory(attributes);
                    break;

                case CustomXMLConstants.FIELD_TAG:
                    handleStarttagField(attributes);
                    break;

                case CustomXMLConstants.METHOD_TAG:
                    handleStarttagMeethod(attributes);
                    break;

                case CustomXMLConstants.ACCESSPATH_TAG:
                    handleStarttagAccesspath(attributes);
                    break;

                case CustomXMLConstants.BASE_TAG:
                    accessPathParentElement = qNameLower;
                    description = attributes.getValue(CustomXMLConstants.DESCRIPTION_ATTRIBUTE);
                    break;

                case CustomXMLConstants.RETURN_TAG:
                    accessPathParentElement = qNameLower;
                    description = attributes.getValue(CustomXMLConstants.DESCRIPTION_ATTRIBUTE);
                    break;

                case CustomXMLConstants.PARAM_TAG:
                    handleStarttagParam(attributes, qNameLower);
                    break;

                case CustomXMLConstants.PATHELEMENT_TAG:
                    handleStarttagPathelement(attributes);
                    break;

                case CustomXMLConstants.SIGNATURE_ON_PATH_TAG:
                    handleStarttagSignatureOnPath(attributes);
                    break;

                case CustomXMLConstants.CLASS_NAME_ON_PATH_TAG:
                    handleStarttagClassNameOnPath(attributes);
                    break;

                case CustomXMLConstants.EXCLUDE_CLASS_NAME_TAG:
                    handleStarttagExcludeClassName(attributes);
                    break;
                case CustomXMLConstants.LOCATION_TAG:
                    handleExactLocation(attributes);
                    break;

            }
        }

        protected void handleStarttagCategory(Attributes attributes) {
            String strSysCategory = attributes.getValue(CustomXMLConstants.ID_ATTRIBUTE).trim();
            String strCustomCategory = attributes.getValue(CustomXMLConstants.CUSTOM_ID_ATTRIBUTE);
            if (strCustomCategory != null && !strCustomCategory.isEmpty())
                strCustomCategory = strCustomCategory.trim();
            String strCustomDescription = attributes.getValue(CustomXMLConstants.DESCRIPTION_ATTRIBUTE);
            if (strCustomDescription != null && !strCustomDescription.isEmpty())
                strCustomDescription = strCustomDescription.trim();

            category = getOrMakeCategory(CategoryDefinition.CATEGORY.valueOf(strSysCategory), strCustomCategory, strCustomDescription);

            // Check for excluded categories
            if (categoryFilter != null && !categoryFilter.acceptsCategory(category)) {
                category = null;
            }
        }

        protected void handleStarttagField(Attributes attributes) {
            if (category != null && attributes != null) {
                fieldSignature = parseSignature(attributes);
                accessPathParentElement = CustomXMLConstants.BASE_TAG;
            }
        }

        protected void handleStarttagMeethod(Attributes attributes) {
            if (category != null && attributes != null) {
                methodSignature = parseSignature(attributes);

                // Get the call type
                callType = MethodSourceSinkDefinition.CallType.MethodCall;
                String strCallType = attributes.getValue(CustomXMLConstants.CALL_TYPE);
                if (strCallType != null && !strCallType.isEmpty()) {
                    strCallType = strCallType.trim();
                    if (strCallType.equalsIgnoreCase("MethodCall"))
                        callType = MethodSourceSinkDefinition.CallType.MethodCall;
                    else if (strCallType.equalsIgnoreCase("Callback"))
                        callType = MethodSourceSinkDefinition.CallType.Callback;
                }
            }
        }

        protected void handleStarttagAccesspath(Attributes attributes) {
            if ((methodSignature != null && !methodSignature.isEmpty())
                    || (fieldSignature != null && !fieldSignature.isEmpty())) {
                pathElements = new ArrayList<>();
                pathElementTypes = new ArrayList<>();

                if (attributes != null) {
                    String tempStr = attributes.getValue(CustomXMLConstants.IS_SOURCE_ATTRIBUTE);
                    if (tempStr != null && !tempStr.isEmpty())
                        isSource = tempStr.equalsIgnoreCase(CustomXMLConstants.TRUE);

                    tempStr = attributes.getValue(CustomXMLConstants.IS_SINK_ATTRIBUTE);
                    if (tempStr != null && !tempStr.isEmpty())
                        isSink = tempStr.equalsIgnoreCase(CustomXMLConstants.TRUE);

                    String newDesc = attributes.getValue(CustomXMLConstants.DESCRIPTION_ATTRIBUTE);
                    if (newDesc != null && !newDesc.isEmpty())
                        description = newDesc;
                }
            }
        }

        protected void handleStarttagParam(Attributes attributes, String qNameLower) {
            if ((methodSignature != null || fieldSignature != null) && attributes != null) {
                String tempStr = attributes.getValue(CustomXMLConstants.INDEX_ATTRIBUTE);
                if (tempStr != null && !tempStr.isEmpty())
                    paramIndex = Integer.parseInt(tempStr);

                tempStr = attributes.getValue(CustomXMLConstants.TYPE_ATTRIBUTE);
                if (tempStr != null && !tempStr.isEmpty())
                    paramTypes.add(tempStr.trim());
            }
            accessPathParentElement = qNameLower;
            description = attributes.getValue(CustomXMLConstants.DESCRIPTION_ATTRIBUTE);
        }

        protected void handleStarttagPathelement(Attributes attributes) {
            if (methodSignature != null && attributes != null) {
                String tempStr = attributes.getValue(CustomXMLConstants.FIELD_ATTRIBUTE);
                if (tempStr != null && !tempStr.isEmpty()) {
                    pathElements.add(tempStr);
                }

                tempStr = attributes.getValue(CustomXMLConstants.TYPE_ATTRIBUTE);
                if (tempStr != null && !tempStr.isEmpty()) {
                    pathElementTypes.add(tempStr);
                }
            }
        }

        protected void handleStarttagSignatureOnPath(Attributes attributes) {
            String signature = getStringAttribute(attributes, CustomXMLConstants.SIGNATURE_ATTRIBUTE);
            if (signature != null) {
                if (signaturesOnPath == null)
                    signaturesOnPath = new HashSet<>();
                signaturesOnPath.add("<" + signature + ">");
            }
        }


        protected void handleExactLocation(Attributes attributes) {
            String signature = getStringAttribute(attributes, CustomXMLConstants.METHOD_SIGNATURE_ATTRIBUTE);
            int lineNumber = getIntegerAttribute(attributes, CustomXMLConstants.LINE_NUMBER_ATTRIBUTE);

            if (signature != null) {
                if (stmtLocations == null) {
                    stmtLocations = new HashSet<>();
                }
                if (!signature.contains("<")) {
                    signature =   "<" + signature + ">";
                }
                stmtLocations.add(new StmtLocation(lineNumber, signature));
            }
        }


        protected void handleStarttagClassNameOnPath(Attributes attributes) {
            String className = getStringAttribute(attributes, CustomXMLConstants.CLASS_NAME_ATTRIBUTE);
            if (className != null) {
                if (classNamesOnPath == null)
                    classNamesOnPath = new HashSet<>();
                classNamesOnPath.add(className);
            }
        }

        protected void handleStarttagExcludeClassName(Attributes attributes) {
            String className = getStringAttribute(attributes, CustomXMLConstants.CLASS_NAME_ATTRIBUTE);
            if (className != null) {
                if (excludedClassNames == null)
                    excludedClassNames = new HashSet<>();
                excludedClassNames.add(className);
            }
        }

        /**
         * Reads the method or field signature from the given attribute map
         *
         * @param attributes The attribute map from which to read the signature
         * @return The signature that identifies a Soot method or field
         */
        private String parseSignature(Attributes attributes) {
            String signature = attributes.getValue(CustomXMLConstants.SIGNATURE_ATTRIBUTE).trim();

            // If the user did not specify the brackets, we add them on
            // the fly
            if (signature != null && !signature.isEmpty())
                if (!signature.startsWith("<"))
                    signature = "<" + signature + ">";
            return signature;
        }

        /**
         * PathElement is the only element having values inside, so nothing to do here.
         * Doesn't care at the current state of parsing.
         **/
        @Override
        public void characters(char[] ch, int start, int length) throws SAXException {
        }

        /**
         * Gets a string value from a collection of attributes
         *
         * @param attributes The collection of attributes
         * @param name       The name of the attribute for which to get the value
         * @return The value for the given attribute if such a value exists and is not
         * empty, null otherwise
         */
        private String getStringAttribute(Attributes attributes, String name) {
            String value = attributes.getValue(name);
            if (value != null && !value.isEmpty()) {
                value = value.trim();
                if (!value.isEmpty())
                    return value;
            }
            return null;
        }


        /**
         * Gets a int value from a collection of attributes
         *
         * @param attributes The collection of attributes
         * @param name       The name of the attribute for which to get the value
         * @return The value for the given attribute if such a value exists and is not
         * empty, null otherwise
         */
        private Integer getIntegerAttribute(Attributes attributes, String name) {
            String value = attributes.getValue(name);
            if (value != null && !value.isEmpty()) {
                value = value.trim();
                if (!value.isEmpty()) {
                    try {
                        return Integer.parseInt(value);
                    } catch (NumberFormatException e) {
                        return -1;
                    }
                }
            }
            return -1;
        }


        /**
         * EventHandler for the End of an element. Putting the values into the objects.
         * For additional information: startElement description. Starting with the
         * innerst elements and switching up to the outer elements
         * <p>
         * - pathElement -> means field sensitive, adding SootFields
         */
        @Override
        public void endElement(String uri, String localName, String qName) throws SAXException {
            String qNameLower = qName.toLowerCase();
            switch (qNameLower) {

                case CustomXMLConstants.CATEGORY_TAG:
                    category = null;
                    break;

                case CustomXMLConstants.METHOD_TAG:
                    handleEndtagMethod();
                    break;

                case CustomXMLConstants.FIELD_TAG:
                    handleEndtagField();
                    break;

                case CustomXMLConstants.ACCESSPATH_TAG:
                    handleEndtagAccesspath();
                    break;

                case CustomXMLConstants.BASE_TAG:
                    accessPathParentElement = "";
                    break;

                case CustomXMLConstants.RETURN_TAG:
                    accessPathParentElement = "";
                    break;

                case CustomXMLConstants.PARAM_TAG:
                    accessPathParentElement = "";
                    paramIndex = -1;
                    paramTypes.clear();
                    break;

                case CustomXMLConstants.ADDITIONAL_FLOW_CONDITION_TAG:
                    if (!classNamesOnPath.isEmpty() || !signaturesOnPath.isEmpty()) {
                        AdditionalFlowCondition additionalFlowCondition = new AdditionalFlowCondition(classNamesOnPath,
                                signaturesOnPath, excludedClassNames);
                        // Reset both for a new condition
                        classNamesOnPath = new HashSet<>();
                        signaturesOnPath = new HashSet<>();

                        excludedClassNames = new HashSet<>();

                        if (conditions == null)
                            conditions = new HashSet<>();
                        conditions.add(additionalFlowCondition);
                    }
                    break;
                case CustomXMLConstants.FIXED_LOCATION_TAG:
                    break;

                case CustomXMLConstants.PATHELEMENT_TAG:
                    break;
            }
        }

        protected void handleEndtagMethod() {
            if (methodSignature == null)
                return;

            // Check whether we have data
            if (!baseAPs.isEmpty() || !paramAPs.isEmpty() || !returnAPs.isEmpty()) {
                AndroidMethod tempMeth = AndroidMethod.createFromSignature(methodSignature);

                if (tempMeth != null) {
                    if (stmtLocations != null && stmtLocations.size() > 0) {
                        ExcactMethod excactMethod = new ExcactMethod(tempMeth);
                        excactMethod.setLocations(stmtLocations);
                        tempMeth = excactMethod;
                    }

                    @SuppressWarnings("unchecked")
                    ISourceSinkDefinition ssd = createMethodSourceSinkDefinition(tempMeth, baseAPs,
                            paramAPs.toArray(new Set[0]), returnAPs, callType, category, conditions);
                    addSourceSinkDefinition(methodSignature, ssd);

                } else {
                    logger.error("Invalid method signature: " + methodSignature);
                }
            }

            // Start a new method and discard our old data
            methodSignature = null;
            fieldSignature = null;
            baseAPs = new HashSet<>();
            paramAPs = new ArrayList<>();
            returnAPs = new HashSet<>();
            description = null;
            stmtLocations = new HashSet<>();

            conditions = new HashSet<>();
        }

        protected void handleEndtagField() {
            // Create the field source
            if (!baseAPs.isEmpty()) {
                ISourceSinkDefinition ssd = createFieldSourceSinkDefinition(fieldSignature, baseAPs, conditions);
                ssd.setCategory(category);
                addSourceSinkDefinition(fieldSignature, ssd);
            }

            // Start a new field and discard our old data
            methodSignature = null;
            fieldSignature = null;
            baseAPs = new HashSet<>();
            paramAPs = new ArrayList<>();
            returnAPs = new HashSet<>();
            description = null;
        }

        protected void handleEndtagAccesspath() {
            // Record the access path for the current element
            if (isSource || isSink) {
                // Clean up the path elements
                if (pathElements != null && pathElements.isEmpty() && pathElementTypes != null
                        && pathElementTypes.isEmpty()) {
                    pathElements = null;
                    pathElementTypes = null;
                }

                // Sanity check
                if (pathElements != null && pathElementTypes != null && pathElements.size() != pathElementTypes.size())
                    throw new RuntimeException(
                            String.format("Length mismatch between path elements (%d) and their types (%d)",
                                    pathElements.size(), pathElementTypes.size()));
                if (pathElements == null || pathElements.isEmpty())
                    if (pathElementTypes != null && !pathElementTypes.isEmpty())
                        throw new RuntimeException("Got types for path elements, but no elements (i.e., fields)");

                // Filter the sources and sinks
                SourceSinkType sstype = SourceSinkType.fromFlags(isSink, isSource);
                if (categoryFilter != null)
                    sstype = categoryFilter.filter(category, sstype);

                if (sstype != SourceSinkType.Neither) {
                    AccessPathTuple apt = AccessPathTuple.fromPathElements(pathElements, pathElementTypes, sstype);

                    // Optional description
                    if (description != null && !description.isEmpty())
                        apt.setDescription(description);

                    // Simplify the AP after setting the description for not breaking the generic
                    // source definition
                    apt = apt.simplify();

                    switch (accessPathParentElement) {
                        case CustomXMLConstants.BASE_TAG:
                            baseAPs.add(apt);
                            break;
                        case CustomXMLConstants.RETURN_TAG:
                            returnAPs.add(apt);
                            break;
                        case CustomXMLConstants.PARAM_TAG:
                            while (paramAPs.size() <= paramIndex)
                                paramAPs.add(new HashSet<AccessPathTuple>());
                            paramAPs.get(paramIndex).add(apt);
                    }
                }
            }

            pathElements = null;
            pathElementTypes = null;

            isSource = false;
            isSink = false;
            pathElements = null;
            pathElementTypes = null;

            description = null;
        }

    }

    protected Map<String, ISourceSinkDefinition> sourcesAndSinks;

    protected Set<ISourceSinkDefinition> sources = new HashSet<>();
    protected Set<ISourceSinkDefinition> sinks = new HashSet<>();
    protected AbstractXMLSourceSinkParser.ICategoryFilter categoryFilter = null;

    protected final Map<ISourceSinkCategory, ISourceSinkCategory> categories = new HashMap<>();

    /**
     * gets the category for the given values. If this is the first time such a
     * category is requested, the respective definition is created. Otherwise, the
     * existing one is returned.
     *
     * @param systemCategory    The system-defined category name
     * @param customCategory    The user-defined category name
     * @param customDescription The human-readable description for the custom
     *                          category
     * @return The category definition object for the given category names
     */
    private ISourceSinkCategory getOrMakeCategory(CategoryDefinition.CATEGORY systemCategory, String customCategory,
                                                  String customDescription) {
        // For the key in the map, we ignore the description. We do not want to
        // have the
        // same category id just with different descriptions.

        ISourceSinkCategory keyDef = new CategoryDefinition(systemCategory, customCategory);
        return categories.computeIfAbsent(keyDef,
                d -> new CategoryDefinition(systemCategory, customCategory, customDescription));
    }

    /**
     * Parses the given input stream to obtain the source/sink definitions
     *
     * @param stream The stream whose data to parse
     */
    protected void parseInputStream(InputStream stream) {
        SAXParserFactory pf = SAXParserFactory.newInstance();
        try {
            pf.setFeature("http://apache.org/xml/features/disallow-doctype-decl", true);
            pf.setFeature("http://xml.org/sax/features/external-general-entities", false);
            pf.setFeature("http://xml.org/sax/features/external-parameter-entities", false);
            SAXParser parser = pf.newSAXParser();
            runParse(parser, stream);
        } catch (ParserConfigurationException e) {
            logger.error("Could not parse sources/sinks from stream", e);
        } catch (SAXException e) {
            logger.error("Could not parse sources/sinks from stream", e);
        }
        // Build the source and sink lists
        buildSourceSinkLists();
    }

    /**
     * Builds the lists of sources and sinks from the data that we have parsed
     */
    protected abstract void buildSourceSinkLists();

    /**
     * Runs the parse method on the given parser
     *
     * @param parser Parser to run parse on
     * @param stream Input stream of XML file
     */
    protected abstract void runParse(SAXParser parser, InputStream stream);

    /**
     * Adds a new source or sink definition
     *
     * @param signature The signature of the method or field that is considered a
     *                  source or a sink
     * @param ssd       The source or sink definition
     */
    protected void addSourceSinkDefinition(String signature, IAccessPathBasedSourceSinkDefinition ssd) {
        if (sourcesAndSinks.containsKey(signature))
            sourcesAndSinks.get(signature).merge(ssd);
        else
            sourcesAndSinks.put(signature, ssd);
    }

    public Set<ISourceSinkDefinition> getSources() {
        return sources;
    }

    public Set<ISourceSinkDefinition> getSinks() {
        return sinks;
    }

    protected static InputStream getStream(String fileName) throws IOException {
        File f = new File(fileName);
        if (f.exists())
            return new FileInputStream(f);

        return ResourceUtils.getResourceStream(fileName);
    }

    public Set<ISourceSinkDefinition> getAllMethods() {
        Set<ISourceSinkDefinition> sourcesSinks = new HashSet<>(sources.size() + sinks.size());
        sourcesSinks.addAll(sources);
        sourcesSinks.addAll(sinks);
        return sourcesSinks;
    }

    protected void addSourceSinkDefinition(String signature, ISourceSinkDefinition ssd) {
        if (sourcesAndSinks.containsKey(signature))
            sourcesAndSinks.get(signature).merge(ssd);
        else
            sourcesAndSinks.put(signature, ssd);
    }

    /**
     * Factory method for {@link FieldSourceSinkDefinition} instances
     *
     * @param signature The signature of the target field
     * @param baseAPs   The access paths that shall be considered as sources or
     *                  sinks
     * @return The newly created {@link FieldSourceSinkDefinition} instance
     */
    protected abstract ISourceSinkDefinition createFieldSourceSinkDefinition(String signature,
                                                                             Set<AccessPathTuple> baseAPs);

    /**
     * Factory method for {@link FieldSourceSinkDefinition} instances
     *
     * @param signature  The signature of the target field
     * @param baseAPs    The access paths that shall be considered as sources or
     *                   sinks
     * @param conditions Conditions which has to be true for the definition to be
     *                   valid
     * @return The newly created {@link FieldSourceSinkDefinition} instance
     */
    protected abstract ISourceSinkDefinition createFieldSourceSinkDefinition(String signature,
                                                                             Set<AccessPathTuple> baseAPs, Set<SourceSinkCondition> conditions);

    /**
     * Factory method for {@link MethodSourceSinkDefinition} instances
     *
     * @param method    The method that is to be defined as a source or sink
     * @param baseAPs   The access paths rooted in the base object that shall be
     *                  considered as sources or sinks
     * @param paramAPs  The access paths rooted in parameters that shall be
     *                  considered as sources or sinks. The index in the set
     *                  corresponds to the index of the formal parameter to which
     *                  the respective set of access paths belongs.
     * @param returnAPs The access paths rooted in the return object that shall be
     *                  considered as sources or sinks
     * @param callType  The type of call (normal call, callback, etc.)
     * @return The newly created {@link MethodSourceSinkDefinition} instance
     */
    protected abstract ISourceSinkDefinition createMethodSourceSinkDefinition(AbstractMethodAndClass method,
                                                                              Set<AccessPathTuple> baseAPs, Set<AccessPathTuple>[] paramAPs, Set<AccessPathTuple> returnAPs,
                                                                              MethodSourceSinkDefinition.CallType callType, ISourceSinkCategory category);

    /**
     * Factory method for {@link MethodSourceSinkDefinition} instances
     *
     * @param method     The method that is to be defined as a source or sink
     * @param baseAPs    The access paths rooted in the base object that shall be
     *                   considered as sources or sinks
     * @param paramAPs   The access paths rooted in parameters that shall be
     *                   considered as sources or sinks. The index in the set
     *                   corresponds to the index of the formal parameter to which
     *                   the respective set of access paths belongs.
     * @param returnAPs  The access paths rooted in the return object that shall be
     *                   considered as sources or sinks
     * @param callType   The type of call (normal call, callback, etc.)
     * @param conditions Conditions which has to be true for the definition to be
     *                   valid
     * @return The newly created {@link MethodSourceSinkDefinition} instance
     */
    protected abstract ISourceSinkDefinition createMethodSourceSinkDefinition(AbstractMethodAndClass method,
                                                                              Set<AccessPathTuple> baseAPs, Set<AccessPathTuple>[] paramAPs, Set<AccessPathTuple> returnAPs,
                                                                              MethodSourceSinkDefinition.CallType callType, ISourceSinkCategory category, Set<SourceSinkCondition> conditions);

    /**
     * Reads the method or field signature from the given attribute map
     *
     * @param attributes The attribute map from which to read the signature
     * @return The signature that identifies a Soot method or field
     */
    protected String parseSignature(Attributes attributes) {
        String signature = attributes.getValue(CustomXMLConstants.SIGNATURE_ATTRIBUTE).trim();

        // If the user did not specify the brackets, we add them on
        // the fly
        if (signature != null && !signature.isEmpty())
            if (!signature.startsWith("<"))
                signature = "<" + signature + ">";
        return signature;
    }

}
