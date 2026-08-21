import os
import pytest


pytest.main()
# 生成report报告
os.system('allure generate -o report -c temps')