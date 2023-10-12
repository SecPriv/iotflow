package soot.jimple.infoflow.android.source;

import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import soot.Scene;
import soot.SootMethod;
import soot.Value;
import soot.jimple.*;
import soot.jimple.infoflow.InfoflowManager;
import soot.jimple.infoflow.android.InfoflowAndroidConfiguration;
import soot.jimple.infoflow.android.callbacks.AndroidCallbackDefinition;
import soot.jimple.infoflow.android.data.ExcactMethod;
import soot.jimple.infoflow.android.data.StmtLocation;
import soot.jimple.infoflow.android.resources.controls.AndroidLayoutControl;
import soot.jimple.infoflow.data.AccessPath;
import soot.jimple.infoflow.data.SootMethodAndClass;
import soot.jimple.infoflow.sourcesSinks.definitions.*;
import soot.jimple.infoflow.sourcesSinks.manager.SinkInfo;
import soot.jimple.infoflow.sourcesSinks.manager.SourceInfo;
import soot.jimple.infoflow.util.SystemClassHandler;

import java.util.*;
/*
 Source Sink Manager that consider the location if set in the sources and sinks
 */
public class LocationSourceSinkManager extends AccessPathBasedSourceSinkManager{
    private final Logger logger = LoggerFactory.getLogger(getClass());


    /**
     * Creates a new instance of the {@link AndroidSourceSinkManager} class with
     * either strong or weak matching.
     *
     * @param sources The list of source methods
     * @param sinks   The list of sink methods
     * @param config  The configuration of the data flow analyzer
     */
    public LocationSourceSinkManager(Collection<? extends ISourceSinkDefinition> sources,
                                            Collection<? extends ISourceSinkDefinition> sinks, InfoflowAndroidConfiguration config) {
        super(sources, sinks, config);
    }

    /**
     * Creates a new instance of the {@link AndroidSourceSinkManager} class with
     * strong matching, i.e. the methods in the code must exactly match those in the
     * list.
     *
     * @param sources         The list of source methods
     * @param sinks           The list of sink methods
     * @param callbackMethods The list of callback methods whose parameters are
     *                        sources through which the application receives data
     *                        from the operating system
     * @param config          The configuration of the data flow analyzer
     * @param layoutControls  A map from reference identifiers to the respective
     *                        Android layout controls
     */
    public LocationSourceSinkManager(Collection<? extends ISourceSinkDefinition> sources,
                                            Collection<? extends ISourceSinkDefinition> sinks, Set<AndroidCallbackDefinition> callbackMethods,
                                            InfoflowAndroidConfiguration config, Map<Integer, AndroidLayoutControl> layoutControls) {
        super(sources, sinks, callbackMethods, config, layoutControls);
    }



    @Override
    protected SourceInfo createSourceInfo(Stmt sCallSite, InfoflowManager manager, ISourceSinkDefinition def) {
        if (def instanceof MethodSourceSinkDefinition) {
            SootMethodAndClass methodAndClass = ((MethodSourceSinkDefinition)def).getMethod();
           if (methodAndClass instanceof ExcactMethod) {
                Set<StmtLocation> sourceSinkLocations = ((ExcactMethod) methodAndClass).getLocations();
                if (sourceSinkLocations != null && sourceSinkLocations.size()>0) {
                    try {
                        SootMethod parentMethod = manager.getICFG().getMethodOf(sCallSite);
                        int lineNumber = sCallSite.getJavaSourceStartLineNumber();
                        StmtLocation currentLocation = new StmtLocation(lineNumber, parentMethod.toString());
                        if (!sourceSinkLocations.contains(currentLocation)) {
                            return null;
                        }
                    } catch (RuntimeException e) {
                        logger.debug(String.format("Could not get parent method of %s", sCallSite));
                        return null;
                    }
                }
            }
        }

        return super.createSourceInfo(sCallSite, manager, def);
    }

    @Override
    public SinkInfo getSinkInfo(Stmt sCallSite, InfoflowManager manager, AccessPath sourceAccessPath) {

        SinkInfo sinkInfo =  super.getSinkInfo(sCallSite, manager, sourceAccessPath);

        if (sinkInfo == null) {
            return null;
        }

        ISourceSinkDefinition def = sinkInfo.getDefinition();

        if (def instanceof MethodSourceSinkDefinition) {
            SootMethodAndClass methodAndClass = ((MethodSourceSinkDefinition)def).getMethod();
            if (methodAndClass instanceof ExcactMethod) {
                Set<StmtLocation> sourceSinkLocations = ((ExcactMethod) methodAndClass).getLocations();
                if (sourceSinkLocations != null && sourceSinkLocations.size()>0) {
                    try {

                        SootMethod parentMethod = manager.getICFG().getMethodOf(sCallSite);
                        int lineNumber = sCallSite.getJavaSourceStartLineNumber();
                        StmtLocation currentLocation = new StmtLocation(lineNumber, parentMethod.toString());
                        if (!sourceSinkLocations.contains(currentLocation)) {
                            return null;
                        }
                    } catch (RuntimeException e) {
                        logger.debug(String.format("Could not get parent method of %s", sCallSite));
                        return null;
                    }
                }
            }
        }

        return sinkInfo;

    }

}
