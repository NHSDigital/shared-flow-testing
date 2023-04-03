function setHeaders(messageType) {
    const headerNames = context.getVariable(messageType + ".headers.names");
    const headerNamesString = headerNames + "";
    const headerNamesArray = headerNamesString.slice(1, -1).split(", ");

    const denyList = [
        "authorization",
        "cookie",
        "user-agent"
    ];
    const headersAlreadyLogged = [
        "content-type",
        "content-encoding",
        "content-length",
        "x-request-id",
        "x-correlation-id",
        "host",
        "x-forwarded-port"
    ];
    const headers = {};

    headerNamesArray.forEach(headerName => {
        if (denyList.indexOf(headerName.toLowerCase()) != -1 || headersAlreadyLogged.indexOf(headerName.toLowerCase()) != -1) return;

        const count = context.getVariable(messageType + ".header." + headerName + ".values.count");

        if (count > 1) {
            const headerValue = context.getVariable(messageType + ".header." + headerName + ".values");
            const headerValueString = headerValue + "";
            headers[headerName] = headerValueString.slice(1, -1).split(", ");
        } else {
            headers[headerName] = context.getVariable(messageType + ".header." + headerName);
        }
    });

    context.setVariable(messageType + "-headers", JSON.stringify(headers, null, 2));
}

setHeaders("request");
setHeaders("response");
