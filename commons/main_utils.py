import json

from commons.extract_utils import YamlVariableResolver
from commons.request_utils import RequestUtil,print_log


""" ===================== 用例执行主流程 ===================== """
def stand_case_flow(testinfo):
    """
    case_obj：单条已经替换完变量的完整用例
    执行顺序： 发送请求（前置 解析数据） → 后置 提取变量 → 断言
    """
    # 实例化工具类
    resolver = YamlVariableResolver()

    """ 1.发送请求（前置操作：解析yaml数据） """
    # 解析yaml数据, 将解析后的数据赋值回
    req_info = resolver.variable_resolver(kwargs=testinfo["request"])
    # 单独保存提取规则，不要塞进request请求参数
    extract_rule = testinfo.get("extract", None)
    # 发送请求
    res = RequestUtil().send_all_request(**req_info)  # **testinfo["request"] 等价于传入关键字request下面的参数



    """ 2.后置操作（提取变量存至yaml）"""
    resolver.extract_yaml(extract_rule, res)


    """ 3.断言校验（validate）"""
    if testinfo["validate"] is not None:
        resolver.data_validate(testinfo, res)



