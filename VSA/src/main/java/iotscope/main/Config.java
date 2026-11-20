package iotscope.main;

public class Config {
    public static String ANDROID_JAR_DIR = "./libs/android.jar";

    public static String RESULTDIR = "./valuesetResult/";
    public static String LOGDIR = "./logs/";

    //Default set to true
    public static boolean PARSEINTERFACECALL = true;

    //Default 100
    // Steps after ending backwardcontext
    public static int MAXMETHODCHAINLEN = 50;

    //added to limit the backward steps taken per Value Point -> might not be needed but there are some value points, which are producing always new steps
    public static int MAXBACKWARDSTEPS = 300;
    //250 normal
    //25 -low resources

    public static int MAXBACKWARDCONTEXT = 600;
    //1000 normal
    //100 low

    // Kills the process afterwards
    public static int TIMEOUT_BACKWARDS = 15 * 60; //Seconds
    public static int TIMEOUT_FORWARD = 20 * 60; //Seconds

    public static String GRAPH_RESULT_DIR = "./graph/";
    public static boolean OUTPUT_GRAPHS = false;

}
