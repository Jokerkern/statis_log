import os
import subprocess
import random
import socket


def call(node, module, function, args='[]', cookie="node-cookie", sname=None, lname=None):
    """
    调用远程Erlang节点的函数
    
    参数:
        node: 目标Erlang节点名称
        module: 要调用的模块名称
        function: 要调用的函数名称
        args: 函数参数，会被转换为Erlang列表
        cookie: Erlang节点cookie (默认为"node-cookie")
        sname: 本地短节点名称 (可选)
        lname: 本地长节点名称 (默认为随机生成)
        
    返回:
        远程调用的输出结果（字符串）
    
    抛出:
        Exception: 执行过程中发生的任何错误
    """
    # 构造escript路径
    script_dir = os.path.dirname(os.path.abspath(__file__))
    escript_path = os.path.join(script_dir, 'rpc_call.escript')
    
    # 如果未提供lname，则随机生成
    if lname is None:
        random_id = ''.join([str(random.randint(0, 9)) for _ in range(6)])
        local_ip = socket.gethostbyname(socket.gethostname())
        lname = f"python_erpc_{random_id}@{local_ip}"
    
    # 构造命令行
    cmd = ["escript", escript_path, node, module, function, args]
    
    # 处理可选参数
    env = os.environ.copy()
    escript_opts = []
    if cookie:
        escript_opts.append(f"-setcookie {cookie}")
    if sname:
        escript_opts.append(f"-sname {sname}")
    elif lname:
        escript_opts.append(f"-name {lname}")
    env["ERL_FLAGS"] = " ".join(escript_opts)
    
    # 执行命令
    try:
        result = subprocess.run(cmd, env=env, text=True, capture_output=True)
        if result.returncode != 0:
            raise RuntimeError(f"错误：{result.stderr}")
        return result.stdout.strip()
    except Exception as e:
        raise Exception(f"执行escript时出错：{str(e)}")
