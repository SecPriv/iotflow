package soot.jimple.infoflow.cmd;

import soot.jimple.infoflow.android.CustomSetupApplication;
import soot.jimple.infoflow.android.InfoflowAndroidConfiguration;
import soot.jimple.infoflow.android.SetupApplication;
import soot.jimple.infoflow.android.callbacks.AbstractCallbackAnalyzer;

public class Main extends MainClass {


    public static void main(String[] args) throws Exception {
        Main main = new Main();
        main.run(args);

    }


    /**
     * Creates an instance of the FlowDroid data flow solver tool for Android.
     * Derived classes can override this method to inject custom variants of
     * FlowDroid.
     *
     * @param config The configuration object
     * @return An instance of the data flow solver
     */
    protected SetupApplication createFlowDroidInstance(final InfoflowAndroidConfiguration config) {
        return new CustomSetupApplication(config);
    }
}
