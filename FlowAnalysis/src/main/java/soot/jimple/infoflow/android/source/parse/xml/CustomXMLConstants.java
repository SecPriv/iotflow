package soot.jimple.infoflow.android.source.parsers.xml;

/**
 * Class containing the constant attribute and tag names used in the XML-based
 * source and sink definition files
 *
 * Modified (XMLConstants) XML constants to allow exact method locations.
 *
 */
public class CustomXMLConstants {

    public static final String CATEGORY_TAG = "category";
    public static final String METHOD_TAG = "method";
    public static final String FIELD_TAG = "field";
    public static final String BASE_TAG = "base";
    public static final String RETURN_TAG = "return";
    public static final String PARAM_TAG = "param";
    public static final String ACCESSPATH_TAG = "accesspath";
    public static final String PATHELEMENT_TAG = "pathelement";
    public static final String ADDITIONAL_FLOW_CONDITION_TAG = "additionalflowcondition";
    public static final String SIGNATURE_ON_PATH_TAG = "signatureonpath";
    public static final String CLASS_NAME_ON_PATH_TAG = "classnameonpath";
    public static final String CLASS_NAME_ATTRIBUTE = "className";
    public static final String EXCLUDE_CLASS_NAME_TAG = "excludeclassname";

    public static final String FIXED_LOCATION_TAG = "fixedlocation";
    public static final String LOCATION_TAG = "location";


    public static final String ID_ATTRIBUTE = "id";
    public static final String CUSTOM_ID_ATTRIBUTE = "customId";
    public static final String SIGNATURE_ATTRIBUTE = "signature";
    public static final String CALL_TYPE = "callType";
    public static final String TYPE_ATTRIBUTE = "type";
    public static final String INDEX_ATTRIBUTE = "index";
    public static final String IS_SOURCE_ATTRIBUTE = "isSource";
    public static final String IS_SINK_ATTRIBUTE = "isSink";
    public static final String LENGTH_ATTRIBUTE = "length";
    public static final String FIELD_ATTRIBUTE = "field";
    public static final String DESCRIPTION_ATTRIBUTE = "description";
    public static final String METHOD_SIGNATURE_ATTRIBUTE = "methodSignature";
    public static final String LINE_NUMBER_ATTRIBUTE = "lineNumber";

    public static final String TRUE = "true";

    public static final String TYPE_BOOLEAN = "boolean";
    public static final String TYPE_BYTE = "byte";
    public static final String TYPE_CHAR = "char";
    public static final String TYPE_DOUBLE = "double";
    public static final String TYPE_INT = "int";
    public static final String TYPE_LONG = "long";
    public static final String TYPE_SHORT = "short";

}
