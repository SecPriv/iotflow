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

import heros.solver.Pair;

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



    /**
     * Whether a source/sink definition applies at this statement. Definitions created by IoTFlow for
     * exact statement locations ({@link ExcactMethod}) only match at those locations; all other
     * definitions always match.
     */
    private boolean matchesLocation(Stmt sCallSite, InfoflowManager manager, ISourceSinkDefinition def) {
        if (!(def instanceof MethodSourceSinkDefinition))
            return true;
        SootMethodAndClass methodAndClass = ((MethodSourceSinkDefinition) def).getMethod();
        if (!(methodAndClass instanceof ExcactMethod))
            return true;
        Set<StmtLocation> sourceSinkLocations = ((ExcactMethod) methodAndClass).getLocations();
        if (sourceSinkLocations == null || sourceSinkLocations.isEmpty())
            return true;
        try {
            SootMethod parentMethod = manager.getICFG().getMethodOf(sCallSite);
            int lineNumber = sCallSite.getJavaSourceStartLineNumber();
            return sourceSinkLocations.contains(new StmtLocation(lineNumber, parentMethod.toString()));
        } catch (RuntimeException e) {
            logger.debug(String.format("Could not get parent method of %s", sCallSite));
            return false;
        }
    }

    // FlowDroid 2.14+ allows several definitions per statement; filter them by location
    // (FlowDroid 2.12: createSourceInfo(Stmt, InfoflowManager, ISourceSinkDefinition))
    @Override
    protected Collection<Pair<AccessPath, ISourceSinkDefinition>> createSourceInfoPairs(Stmt sCallSite,
            InfoflowManager manager, Collection<ISourceSinkDefinition> defs) {
        List<ISourceSinkDefinition> matching = new ArrayList<>();
        for (ISourceSinkDefinition def : defs)
            if (matchesLocation(sCallSite, manager, def))
                matching.add(def);
        if (matching.isEmpty())
            return Collections.emptySet();
        return super.createSourceInfoPairs(sCallSite, manager, matching);
    }

    @Override
    public SinkInfo getSinkInfo(Stmt sCallSite, InfoflowManager manager, AccessPath sourceAccessPath) {
        SinkInfo sinkInfo = super.getSinkInfo(sCallSite, manager, sourceAccessPath);
        if (sinkInfo == null)
            return null;
        Collection<ISourceSinkDefinition> defs = sinkInfo.getDefinitions();
        if (defs == null || defs.isEmpty())
            return sinkInfo;
        List<ISourceSinkDefinition> matching = new ArrayList<>();
        for (ISourceSinkDefinition def : defs)
            if (matchesLocation(sCallSite, manager, def))
                matching.add(def);
        if (matching.isEmpty())
            return null;
        return matching.size() == defs.size() ? sinkInfo : new SinkInfo(matching, sinkInfo.getUserData());
    }

}
