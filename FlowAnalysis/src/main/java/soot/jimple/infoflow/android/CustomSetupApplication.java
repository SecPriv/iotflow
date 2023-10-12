package soot.jimple.infoflow.android;

import org.xml.sax.SAXException;
import org.xmlpull.v1.XmlPullParserException;
import soot.jimple.infoflow.android.callbacks.AndroidCallbackDefinition;
import soot.jimple.infoflow.android.resources.LayoutFileParser;
import soot.jimple.infoflow.android.results.xml.InfoflowResultsSerializer;
import soot.jimple.infoflow.android.source.*;
import soot.jimple.infoflow.android.source.parsers.xml.XMLSourceSinkParser;
import soot.jimple.infoflow.ipc.IIPCManager;
import soot.jimple.infoflow.results.InfoflowResults;
import soot.jimple.infoflow.rifl.RIFLSourceSinkDefinitionProvider;
import soot.jimple.infoflow.solver.cfg.IInfoflowCFG;
import soot.jimple.infoflow.sourcesSinks.definitions.ISourceSinkDefinitionProvider;
import soot.jimple.infoflow.sourcesSinks.manager.ISourceSinkManager;

import javax.xml.stream.XMLStreamException;
import java.io.IOException;
import java.util.Set;
/*
 Setup application that uses the custom source sink manager
 */
public class CustomSetupApplication extends SetupApplication {
    public CustomSetupApplication(InfoflowAndroidConfiguration config) {
        super(config);
    }

    public CustomSetupApplication(String androidJar, String apkFileLocation) {
        super(androidJar, apkFileLocation);
    }

    public CustomSetupApplication(String androidJar, String apkFileLocation, IIPCManager ipcManager) {
        super(androidJar, apkFileLocation, ipcManager);
    }

    public CustomSetupApplication(InfoflowAndroidConfiguration config, IIPCManager ipcManager) {
        super(config, ipcManager);
    }

    protected ISourceSinkManager createSourceSinkManager(LayoutFileParser lfp,
                                                         Set<AndroidCallbackDefinition> callbacks) {
        LocationSourceSinkManager sourceSinkManager = new LocationSourceSinkManager(
                this.sourceSinkProvider.getSources(), this.sourceSinkProvider.getSinks(), callbacks, config,
                lfp == null ? null : lfp.getUserControlsByID());

        sourceSinkManager.setAppPackageName(this.manifest.getPackageName());
        sourceSinkManager.setResourcePackages(this.resources.getPackages());
        return sourceSinkManager;
    }


    /**
     * Runs the data flow analysis.
     *
     * @throws IOException            Thrown if the given source/sink file could not
     *                                be read.
     * @throws XmlPullParserException Thrown if the Android manifest file could not
     *                                be read.
     */
    public InfoflowResults runInfoflow() throws IOException, XmlPullParserException {
        // If we don't have a source/sink file by now, we cannot run the data
        // flow analysis
        String sourceSinkFile = config.getAnalysisFileConfig().getSourceSinkFile();
        if (sourceSinkFile == null || sourceSinkFile.isEmpty())
            throw new RuntimeException("No source/sink file specified for the data flow analysis");
        String fileExtension = sourceSinkFile.substring(sourceSinkFile.lastIndexOf("."));
        fileExtension = fileExtension.toLowerCase();

        ISourceSinkDefinitionProvider parser = null;
        try {
            if (fileExtension.equals(".xml")) {
                parser = CustomXMLSourceSinkParser.fromFile(sourceSinkFile,
                        new ConfigurationBasedCategoryFilter(config.getSourceSinkConfig()));
            } else if (fileExtension.equals(".txt"))
                parser = SourceSinkListParser.fromFile(sourceSinkFile);
            else if (fileExtension.equals(".rifl"))
                parser = new RIFLSourceSinkDefinitionProvider(sourceSinkFile);
            else
                throw new UnsupportedSourceSinkFormatException("The Inputfile isn't a .txt or .xml file.");
        } catch (SAXException ex) {
            throw new IOException("Could not read XML file", ex);
        }

        return runInfoflow(parser);
    }

    @Override
    protected void serializeResults(InfoflowResults results, IInfoflowCFG cfg) {
        String resultsFile = this.config.getAnalysisFileConfig().getOutputFile();
        if (resultsFile != null && !resultsFile.isEmpty()) {
            InfoflowResultsSerializer serializer = new InfoflowResultsSerializer(cfg, this.config);

            try {
                serializer.serialize(results, resultsFile);
            } catch (IOException e) {
                System.err.println("Could not write data flow results to file: " + e.getMessage());
                e.printStackTrace();
            } catch (XMLStreamException e) {
                System.err.println("Could not write data flow results to file: " + e.getMessage());
                e.printStackTrace();
            }
        }


    }


}
