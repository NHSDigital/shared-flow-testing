def get_variable_from_trace(debug, session_name, variable):
    trace_ids = debug.get_transaction_data(session_name=session_name)
    trace_data = debug.get_transaction_data_by_id(
        session_name=session_name, transaction_id=trace_ids[0]
    )

    return debug.get_apigee_variable_from_trace(name=variable, data=trace_data)
