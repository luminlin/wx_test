# 创建 fixture, 自动管理fixture
import pytest

from commons.extract_utils import clear_yaml
from configs import setting

"""  
第一参数（作用域）：
    function(默认，函数):每个函数之前和之后执行;
    class(类):每个类之前和之后执行;
    module(模块):每个py模块之前和之后执行;
    package/session(包):每个会话之前和之后执行;
第二参数： True/Flase：自动/手动执行
"""

# 每一次执行前清空 extract.yaml
@pytest.fixture(scope="session", autouse=True)
def clear_extract_yaml():
    clear_yaml(setting.extract_path)



# @pytest.fixture(scope='function',autouse=False)
# def execute_sql(request):
#     print('函数之前执行sQL查询!')
#     yield
#     print('函数之后关闭数据库连接!')

