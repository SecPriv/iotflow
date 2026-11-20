package iotscope.forwardexec.objectSimulation.coap;

import iotscope.forwardexec.objectSimulation.SimulationObjects;
import iotscope.forwardexec.objectSimulation.SimulationUtil;
import okhttp3.HttpUrl;
import okhttp3.Request;
import org.eclipse.californium.core.CoapClient;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import soot.Value;
import soot.jimple.AssignStmt;
import soot.jimple.InstanceInvokeExpr;
import soot.jimple.InvokeExpr;
import soot.jimple.InvokeStmt;

import java.net.URL;
import java.util.*;

public class CaliforniumCoapClientSimulation implements SimulationObjects {


    private static final Logger LOGGER = LoggerFactory.getLogger(CaliforniumCoapClientSimulation.class);


    public CaliforniumCoapClientSimulation() {
    }

    @Override
    public HashSet<?> handleAssignNewExpression(AssignStmt stmt, Value rightop, HashMap<Value, HashSet<?>> currentValues) {

        return null;
    }


    @Override
    public HashSet<?> handleInvokeStmt(InvokeStmt stmt, String signature, InvokeExpr expr, HashMap<Value, HashSet<?>> currentValues) {
        if (signature.contains("<org.eclipse.californium.core.CoapClient$Builder: void <init>(java.lang.String,int)>")) {
            HashSet<CoapClient.Builder> coapClient = new HashSet<>();
            List<String> arg0 = new ArrayList<>(SimulationUtil.getStringContent(expr.getArg(0), currentValues));
            List<Integer> arg1 = new ArrayList<>(SimulationUtil.getIntContent(expr.getArg(1), currentValues));
            while (arg0.size() < arg1.size()) {
                arg0.add("");
            }
            while (arg1.size() < arg0.size()) {
                arg1.add(0);
            }
            Iterator<String> arg0Iterator = arg0.iterator();
            Iterator<Integer> arg1Iterator = arg1.iterator();

            while (arg0Iterator.hasNext() && arg1Iterator.hasNext()) {
                coapClient.add(new CoapClient.Builder(arg0Iterator.next(), arg1Iterator.next()));
            }

            return coapClient;
        }
        return null;
    }

    @Override
    public HashSet<?> handleAssignInvokeExpression(AssignStmt stmt, String signature, InvokeExpr expr, HashMap<Value, HashSet<?>> currentValues) {
        if (signature.contains("org.eclipse.californium")) {
            HashSet<CoapClient.Builder> coapClient = new HashSet<>();
            switch (signature) {
                case "<org.eclipse.californium.core.CoapClient$Builder: org.eclipse.californium.core.CoapClient$Builder host(java.lang.String)>": {
                    Value from = ((InstanceInvokeExpr) expr).getBase();
                    HashSet<CoapClient.Builder> coapBuilders = SimulationUtil.getCoapClientBuilder(from, currentValues);
                    HashSet<String> hostValues = SimulationUtil.getStringContent(expr.getArg(0), currentValues);
                    List<String> hostList = Arrays.asList(hostValues.toArray(new String[]{}));
                    int i = 0;
                    for (CoapClient.Builder b : coapBuilders) {
                        if (b != null) {
                            coapClient.add(b.host(hostList.get(i % hostList.size())));
                            i++;
                        }
                    }
                }
                break;
                case "<org.eclipse.californium.core.CoapClient$Builder: org.eclipse.californium.core.CoapClient$Builder path(java.lang.String[])>": {
                    Value from = ((InstanceInvokeExpr) expr).getBase();
                    HashSet<CoapClient.Builder> coapBuilders = SimulationUtil.getCoapClientBuilder(from, currentValues);
                    HashSet<List<String>> pathValues = SimulationUtil.getStringArrayContent(expr.getArg(0), currentValues);
                    List<String[]> hostList = new ArrayList<>();
                    for (List<String> current : pathValues) {
                        hostList.add(current.toArray(new String[]{}));
                    }
                    int i = 0;
                    for (CoapClient.Builder b : coapBuilders) {
                        if (b != null) {
                            coapClient.add(b.path(hostList.get(i % hostList.size())));
                            i++;
                        }
                    }
                }
                break;
                case "<org.eclipse.californium.core.CoapClient$Builder: org.eclipse.californium.core.CoapClient$Builder port(int)>": {
                    Value from = ((InstanceInvokeExpr) expr).getBase();
                    HashSet<CoapClient.Builder> coapBuilders = SimulationUtil.getCoapClientBuilder(from, currentValues);
                    HashSet<Integer> portValues = SimulationUtil.getIntContent(expr.getArg(0), currentValues);
                    List<Integer> portList = Arrays.asList(portValues.toArray(new Integer[]{}));
                    int i = 0;
                    for (CoapClient.Builder b : coapBuilders) {
                        if (b != null) {
                            coapClient.add(b.port(portList.get(i % portList.size())));
                            i++;
                        }
                    }

                    break;
                }
                case "<org.eclipse.californium.core.CoapClient$Builder: org.eclipse.californium.core.CoapClient$Builder query(java.lang.String[])>": {
                    Value from = ((InstanceInvokeExpr) expr).getBase();
                    HashSet<CoapClient.Builder> coapBuilders = SimulationUtil.getCoapClientBuilder(from, currentValues);
                    HashSet<List<String>> pathValues = SimulationUtil.getStringArrayContent(expr.getArg(0), currentValues);
                    List<String[]> hostList = new ArrayList<>();
                    for (List<String> current : pathValues) {
                        hostList.add(current.toArray(new String[]{}));
                    }
                    int i = 0;
                    for (CoapClient.Builder b : coapBuilders) {
                        if (b != null) {
                            coapClient.add(b.query(hostList.get(i % hostList.size())));
                            i++;
                        }
                    }
                    break;
                }
                case "<org.eclipse.californium.core.CoapClient$Builder: org.eclipse.californium.core.CoapClient$Builder scheme(java.lang.String)>": {
                    Value from = ((InstanceInvokeExpr) expr).getBase();
                    HashSet<CoapClient.Builder> coapBuilders = SimulationUtil.getCoapClientBuilder(from, currentValues);
                    HashSet<String> schemeValues = SimulationUtil.getStringContent(expr.getArg(0), currentValues);
                    List<String> schemeList = Arrays.asList(schemeValues.toArray(new String[]{}));
                    int i = 0;
                    for (CoapClient.Builder b : coapBuilders) {
                        if (b != null) {
                            coapClient.add(b.scheme(schemeList.get(i % schemeList.size())));
                            i++;
                        }
                    }
                }
                break;
                case "<org.eclipse.californium.core.CoapClient: org.eclipse.californium.core.CoapClient$Builder create()>": {
                    Value from = ((InstanceInvokeExpr) expr).getBase();
                    HashSet<CoapClient.Builder> coapBuilders = SimulationUtil.getCoapClientBuilder(from, currentValues);
                    HashSet<CoapClient> result = new HashSet<>();
                    for (CoapClient.Builder b : coapBuilders) {
                        if (b != null) {
                            result.add(b.create());
                        }
                    }

                    return result;
                }
                default:
                    LOGGER.error("{} is currently not supported by the OkHttpSimulation", signature);
                    break;
            }
            return coapClient;
        }
        return null;
    }


    @Override
    public HashSet<?> handleAssignConstant(AssignStmt stmt, Value rightop, Value leftOp, HashMap<Value, HashSet<?>> currentValues) {
        return null;
    }

    @Override
    public HashSet<?> handleAssignNewArrayExpr(AssignStmt stmt, Value rightop, HashMap<Value, HashSet<?>> currentValues) {

        return null;
    }

    @Override
    public HashSet<?> handleAssignArithmeticExpr(AssignStmt stmt, Value rightop, HashMap<Value, HashSet<?>> currentValues) {
        return null;
    }


    private HashSet<CoapClient.Builder> initBuilder() {
        HashSet<CoapClient.Builder> tmp = new HashSet<>();
        tmp.add(new CoapClient.Builder("", 0));
        return tmp;
    }


    //base    , destination
    private HashSet<HttpUrl> build(Value from, HashMap<Value, HashSet<?>> currentValues) {
        HashSet<HttpUrl.Builder> values = SimulationUtil.getHttpUrlBuilder(from, currentValues);

        HashSet<HttpUrl> result = new HashSet<>();

        values.forEach(u -> {
            if (u != null) {
                try {
                    result.add(u.build());
                } catch (IllegalStateException e) {
                    LOGGER.error("{} some value might not be defined \n", u);
                }
            }
        });
        return result;

    }


    private HashSet<String> toString(Value from, HashMap<Value, HashSet<?>> currentValues) {
        HashSet<HttpUrl.Builder> builders = SimulationUtil.getHttpUrlBuilder(from, currentValues);
        HashSet<String> newValues = new HashSet<>();

        for (HttpUrl.Builder builder : builders) {
            if (builder == null) {
                continue;
            }
            newValues.add(builder.toString());
        }
        return newValues;


    }


    private HashSet<URL> toURL(Value from, HashMap<Value, HashSet<?>> currentValues) {
        HashSet<URL> newValues = new HashSet<>();
        HashSet<HttpUrl> builders = SimulationUtil.getHttpUrl(from, currentValues);

        for (HttpUrl builder : builders) {
            if (builder == null) {
                continue;
            }
            newValues.add(builder.url());
        }
        return newValues;


    }


    private HashSet<HttpUrl> url(Value from, HashMap<Value, HashSet<?>> currentValues) {
        HashSet<Request> request = SimulationUtil.getOkHttpRequest(from, currentValues);
        HashSet<HttpUrl> newValues = new HashSet<>();
        for (Request r : request) {
            if (r == null) {
                continue;
            }
            newValues.add(r.url());
        }

        return newValues;
    }


    private HashSet<HttpUrl.Builder> query(Value from, HashSet<String> schemeValues, HashMap<Value, HashSet<?>> currentValues) {
        List<HttpUrl.Builder> builders = Arrays.asList(SimulationUtil.getHttpUrlBuilder(from, currentValues).toArray(new HttpUrl.Builder[]{}));
        int i = 0;

        HashSet<HttpUrl.Builder> newValues = new HashSet<>();
        for (String value : schemeValues) {
            if (value == null) {
                continue;
            }
            if (i < builders.size()) {
                newValues.add(builders.get(i).query(value));
            } else {
                newValues.add(new HttpUrl.Builder().query(value));
            }
            i++;
        }
        return newValues;

    }


    private HashSet<HttpUrl.Builder> port(Value from, HashSet<Integer> schemeValues, HashMap<Value, HashSet<?>> currentValues) {
        List<HttpUrl.Builder> builders = Arrays.asList(SimulationUtil.getHttpUrlBuilder(from, currentValues).toArray(new HttpUrl.Builder[]{}));
        int i = 0;


        HashSet<HttpUrl.Builder> newValues = new HashSet<>();
        for (Integer value : schemeValues) {
            if (value == null || value < 1) {
                continue;
            }
            if (i < builders.size()) {
                newValues.add(builders.get(i).port(value));
            } else {
                newValues.add(new HttpUrl.Builder().port(value));
            }

            i++;
        }

        return newValues;
    }


    private HashSet<HttpUrl.Builder> fragment(Value from, HashSet<String> schemeValues, HashMap<Value, HashSet<?>> currentValues) {
        List<HttpUrl.Builder> builders = Arrays.asList(SimulationUtil.getHttpUrlBuilder(from, currentValues).toArray(new HttpUrl.Builder[]{}));
        int i = 0;

        HashSet<HttpUrl.Builder> newValues = new HashSet<>();
        for (String value : schemeValues) {
            if (value == null) {
                continue;
            }
            if (i < builders.size()) {
                newValues.add(builders.get(i).fragment(value));
            } else {
                newValues.add(new HttpUrl.Builder().fragment(value));
            }
            i++;

        }

        return newValues;
    }

    private HashSet<HttpUrl.Builder> password(Value from, HashSet<String> schemeValues, HashMap<Value, HashSet<?>> currentValues) {
        List<HttpUrl.Builder> builders = Arrays.asList(SimulationUtil.getHttpUrlBuilder(from, currentValues).toArray(new HttpUrl.Builder[]{}));
        int i = 0;

        HashSet<HttpUrl.Builder> newValues = new HashSet<>();
        for (String value : schemeValues) {
            if (value == null) {
                continue;
            }
            if (i < builders.size()) {
                newValues.add(builders.get(i).password(value));
            } else {
                newValues.add(new HttpUrl.Builder().password(value));
            }
            i++;
        }

        return newValues;
    }

    private HashSet<HttpUrl.Builder> encodedQuery(Value from, HashSet<String> schemeValues, HashMap<Value, HashSet<?>> currentValues) {
        List<HttpUrl.Builder> builders = Arrays.asList(SimulationUtil.getHttpUrlBuilder(from, currentValues).toArray(new HttpUrl.Builder[]{}));
        int i = 0;

        HashSet<HttpUrl.Builder> newValues = new HashSet<>();
        for (String value : schemeValues) {
            if (value == null) {
                continue;
            }

            if (i < builders.size()) {
                newValues.add(builders.get(i).encodedQuery(value));
            } else {
                newValues.add(new HttpUrl.Builder().encodedQuery(value));
            }
            i++;
        }
        return newValues;
    }


    private HashSet<HttpUrl.Builder> encodedPath(Value from, HashSet<String> schemeValues, HashMap<Value, HashSet<?>> currentValues) {
        List<HttpUrl.Builder> builders = Arrays.asList(SimulationUtil.getHttpUrlBuilder(from, currentValues).toArray(new HttpUrl.Builder[]{}));
        int i = 0;

        HashSet<HttpUrl.Builder> newValues = new HashSet<>();
        for (String value : schemeValues) {
            if (value == null) {
                continue;
            }
            try {
                if (i < builders.size()) {
                    newValues.add(builders.get(i).encodedPath(value));
                } else {
                    newValues.add(new HttpUrl.Builder().encodedPath(value));
                }
            } catch (IllegalArgumentException e) {
                if (i < builders.size()) {
                    newValues.add(builders.get(i));
                }
                LOGGER.error("Invalid encodedPath to add to the HttpUrlBuilder");
            }

            i++;
        }
        return newValues;
    }

    private HashSet<HttpUrl.Builder> encodedPassword(Value from, HashSet<String> schemeValues, HashMap<Value, HashSet<?>> currentValues) {
        List<HttpUrl.Builder> builders = Arrays.asList(SimulationUtil.getHttpUrlBuilder(from, currentValues).toArray(new HttpUrl.Builder[]{}));
        int i = 0;

        HashSet<HttpUrl.Builder> newValues = new HashSet<>();
        for (String value : schemeValues) {
            if (value == null) {
                continue;
            }
            if (i < builders.size()) {
                newValues.add(builders.get(i).encodedPassword(value));
            } else {
                newValues.add(new HttpUrl.Builder().encodedPassword(value));
            }
            i++;
        }
        return newValues;
    }

    private HashSet<HttpUrl.Builder> encodedFragment(Value from, HashSet<String> schemeValues, HashMap<Value, HashSet<?>> currentValues) {
        List<HttpUrl.Builder> builders = Arrays.asList(SimulationUtil.getHttpUrlBuilder(from, currentValues).toArray(new HttpUrl.Builder[]{}));
        int i = 0;


        HashSet<HttpUrl.Builder> newValues = new HashSet<>();
        for (String value : schemeValues) {
            if (value == null) {
                continue;
            }
            if (i < builders.size()) {
                newValues.add(builders.get(i).encodedFragment(value));
            } else {
                newValues.add(new HttpUrl.Builder().encodedFragment(value));
            }
            i++;
        }
        return newValues;
    }

    private HashSet<HttpUrl.Builder> addEncodedQueryParameter(Value from, HashSet<String> param0, HashSet<String> param1, HashMap<Value, HashSet<?>> currentValues) {
        List<HttpUrl.Builder> builders = Arrays.asList(SimulationUtil.getHttpUrlBuilder(from, currentValues).toArray(new HttpUrl.Builder[]{}));
        int i = 0;


        HashSet<HttpUrl.Builder> newValues = new HashSet<>();
        for (String value0 : param0) {
            for (String value1 : param1) {
                if (value0 == null || value1 == null) {
                    continue;
                }
                if (i < builders.size()) {
                    newValues.add(builders.get(i).addEncodedQueryParameter(value0, value1));
                } else {
                    newValues.add(new HttpUrl.Builder().addEncodedQueryParameter(value0, value1));
                }

            }
            i++;
        }
        return newValues;
    }

    private HashSet<HttpUrl.Builder> addEncodedPathSegments(Value from, HashSet<String> schemeValues, HashMap<Value, HashSet<?>> currentValues) {
        List<HttpUrl.Builder> builders = Arrays.asList(SimulationUtil.getHttpUrlBuilder(from, currentValues).toArray(new HttpUrl.Builder[]{}));
        int i = 0;

        HashSet<HttpUrl.Builder> newValues = new HashSet<>();
        for (String value : schemeValues) {
            if (value == null) {
                continue;
            }
            if (i < builders.size()) {
                newValues.add(builders.get(i).addEncodedPathSegments(value));
            } else {
                newValues.add(new HttpUrl.Builder().addEncodedPathSegments(value));
            }
            i++;
        }
        return newValues;
    }

    private HashSet<HttpUrl.Builder> addEncodedPathSegment(Value from, HashSet<String> schemeValues, HashMap<Value, HashSet<?>> currentValues) {
        List<HttpUrl.Builder> builders = Arrays.asList(SimulationUtil.getHttpUrlBuilder(from, currentValues).toArray(new HttpUrl.Builder[]{}));
        int i = 0;

        HashSet<HttpUrl.Builder> newValues = new HashSet<>();
        for (String value : schemeValues) {
            if (value == null) {
                continue;
            }
            if (i < builders.size()) {
                newValues.add(builders.get(i).addEncodedPathSegment(value));
            } else {
                newValues.add(new HttpUrl.Builder().addEncodedPathSegment(value));
            }

            i++;
        }
        return newValues;
    }


    private HashSet<HttpUrl.Builder> addQueryParameter(Value from, HashSet<String> param0, HashSet<String> param1, HashMap<Value, HashSet<?>> currentValues) {
        List<HttpUrl.Builder> builders = Arrays.asList(SimulationUtil.getHttpUrlBuilder(from, currentValues).toArray(new HttpUrl.Builder[]{}));
        int i = 0;

        HashSet<HttpUrl.Builder> newValues = new HashSet<>();
        for (String value0 : param0) {
            for (String value1 : param1) {
                if (value0 == null || value1 == null) {
                    continue;
                }
                if (i < builders.size()) {
                    newValues.add(builders.get(i).addQueryParameter(value0, value1));
                } else {
                    newValues.add(new HttpUrl.Builder().addQueryParameter(value0, value1));
                }

            }
            i++;
        }
        return newValues;
    }

    private HashSet<HttpUrl.Builder> encodedUsername(Value from, HashSet<String> schemeValues, HashMap<Value, HashSet<?>> currentValues) {
        List<HttpUrl.Builder> builders = Arrays.asList(SimulationUtil.getHttpUrlBuilder(from, currentValues).toArray(new HttpUrl.Builder[]{}));
        int i = 0;

        HashSet<HttpUrl.Builder> newValues = new HashSet<>();
        for (String value : schemeValues) {
            if (value == null) {
                continue;
            }
            if (i < builders.size()) {
                newValues.add(builders.get(i).encodedUsername(value));
            } else {
                newValues.add(new HttpUrl.Builder().encodedUsername(value));
            }
            i++;
        }
        return newValues;
    }

    private HashSet<HttpUrl.Builder> addPathSegment(Value from, HashSet<String> schemeValues, HashMap<Value, HashSet<?>> currentValues) {
        List<HttpUrl.Builder> builders = Arrays.asList(SimulationUtil.getHttpUrlBuilder(from, currentValues).toArray(new HttpUrl.Builder[]{}));
        int i = 0;

        HashSet<HttpUrl.Builder> newValues = new HashSet<>();
        for (String value : schemeValues) {
            if (value == null) {
                continue;
            }
            if (i < builders.size()) {
                newValues.add(builders.get(i).addPathSegment(value));
            } else {
                newValues.add(new HttpUrl.Builder().addPathSegment(value));
            }
            i++;
        }
        return newValues;
    }


    private HashSet<HttpUrl.Builder> host(Value from, HashSet<String> schemeValues, HashMap<Value, HashSet<?>> currentValues) {
        List<HttpUrl.Builder> builders = Arrays.asList(SimulationUtil.getHttpUrlBuilder(from, currentValues).toArray(new HttpUrl.Builder[]{}));
        int i = 0;

        HashSet<HttpUrl.Builder> newValues = new HashSet<>();
        for (String value : schemeValues) {
            if (value == null) {
                continue;
            }
            try {
                if (i < builders.size()) {
                    newValues.add(builders.get(i).host(value));
                } else {
                    newValues.add(new HttpUrl.Builder().host(value));
                }
            } catch (IllegalArgumentException e) {
                if (i < builders.size()) {
                    newValues.add(builders.get(i));
                }
                LOGGER.error("Invalid host to add to the HttpUrlBuilder");
            }

            i++;
        }
        return newValues;
    }

    private HashSet<HttpUrl.Builder> scheme(Value from, HashSet<String> schemeValues, HashMap<Value, HashSet<?>> currentValues) {
        List<HttpUrl.Builder> builders = Arrays.asList(SimulationUtil.getHttpUrlBuilder(from, currentValues).toArray(new HttpUrl.Builder[]{}));
        int i = 0;

        HashSet<HttpUrl.Builder> newValues = new HashSet<>();
        for (String value : schemeValues) {
            if (value == null) {
                continue;
            }
            try {
                if (i < builders.size()) {
                    newValues.add(builders.get(i).scheme(value));
                } else {
                    newValues.add(new HttpUrl.Builder().scheme(value));
                }
            } catch (IllegalArgumentException e) {
                if (i < builders.size()) {
                    newValues.add(builders.get(i));
                }
                LOGGER.error("Invalid scheme to add to the HttpUrlBuilder");
            }

            i++;
        }
        return newValues;
    }


}
