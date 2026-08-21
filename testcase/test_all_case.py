import allure
import pytest

from commons.ddt_utils import read_all_testcase
from commons.main_utils import stand_case_flow
from commons.request_utils import print_log
from configs import setting

@allure.epic(setting.allure_project_name)
class TestApi:

    # 多个装饰器，按顺序依次执行
    @pytest.mark.smoke  # 自义定标记      # (下一个)数据驱动方法：参数名，数据(列表/元组)
    @pytest.mark.parametrize("testinfo", read_all_testcase(setting.test_yaml_path))
    def test_api(self, testinfo):

        print_log(f"========== 开始执行用例：{testinfo['title']} ==========")
        print(testinfo["title"])

        # 设置Allure报告用例名称
        allure.dynamic.title(testinfo["title"])
        allure.dynamic.feature(testinfo["feature"])
        allure.dynamic.story(testinfo["story"])

        # 执行用例流程
        stand_case_flow(testinfo)





