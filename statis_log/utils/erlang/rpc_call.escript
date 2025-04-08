#!/usr/bin/env escript

main(Args) ->
    case parse_args(Args) of
        {ok, NodeName, Module, Function, ArgsString} ->
            try
                % 连接到目标节点
                Node = list_to_atom(NodeName),
                % 解析参数字符串
                FunctionArgs = parse_function_args(ArgsString),
                % 执行rpc调用
                Result = rpc:call(Node, list_to_atom(Module), list_to_atom(Function), FunctionArgs),
                io:format("~p~n", [Result])
            catch
                error:Reason ->
                    io:format(standard_error, "Error: ~p~n", [Reason]),
                    halt(1);
                exit:Reason ->
                    io:format(standard_error, "Exit: ~p~n", [Reason]),
                    halt(2)
            end;
        {error, Reason} ->
            io:format(standard_error, "Error: ~s~n", [Reason]),
            usage(),
            halt(1)
    end.

parse_args([NodeName, Module, Function, ArgsString]) ->
    {ok, NodeName, Module, Function, ArgsString};
parse_args([NodeName, Module, Function]) ->
    {ok, NodeName, Module, Function, "[]"};
parse_args(_) ->
    {error, "Invalid arguments"}.

usage() ->
    io:format(standard_error, "Usage: rpc_call.escript <node_name> <module> <function> [args_as_list_string]~n", []),
    io:format(standard_error, "Example: rpc_call.escript 'mynode@host' 'erlang' 'node' '[]'~n", []),
    io:format(standard_error, "Example: rpc_call.escript 'mynode@host' 'application' 'which_applications' '[]'~n", []).

parse_function_args(ArgsString) ->
    % 这里简单地执行字符串解析，真实场景可能需要更健壮的解析方式
    {ok, Tokens, _} = erl_scan:string(ArgsString ++ "."),
    {ok, Args} = erl_parse:parse_term(Tokens),
    Args. 