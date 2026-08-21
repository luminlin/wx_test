# 接口关联封装（提取变量），处理 管理所有接口关联的中间值 的extract.yaml文件
import json
import random
import re
import jsonpath
import yaml

from configs import setting
from commons.request_utils import print_log

""" ========= yaml文件的写入、读取、清空 ========= """
# 接口关联的中间值 写入
def write_yaml(data, path):
    with open(path, encoding="utf-8", mode="a+") as file:  # a+ 追加
        yaml.safe_dump(data, stream=file, allow_unicode=True)

# 读取
def read_yaml(path):
    with open(path, encoding="utf-8", mode="r") as file:
        all_value = yaml.safe_load(file)   # 读取全部数据
        return all_value

# 清空
def clear_yaml(path):
    with open(path, encoding="utf-8", mode="w") as file:
        pass



class YamlVariableResolver:  # 解决yaml变量

    """ =============== 1.解析yaml数据中的变量引用 ================= """
    def yaml_variables(self, yaml_data):
        # 三元表达式
        # yaml_data_str = yaml_data if isinstance(yaml_data,str) else json.dumps(yaml_data,ensure_ascii=False)
        if isinstance(yaml_data, str):  # 判断是否 字符串
            yaml_data_str = yaml_data
            # print(f'解析前:{yaml_data_str}')
            for _ in range(yaml_data_str.count('${')):  # '_' 占位符，不需要用到该参数
                if '${' in yaml_data_str and '}' in yaml_data_str:
                    start_index = yaml_data_str.find('$')
                    end_index = yaml_data_str.find('}', start_index)
                    variable_data = yaml_data_str[
                        start_index:end_index + 1]  # Python 切片规则 [起始:结束)，结束下标不包含，所以要 end_index+1 才能把 } 包含进截取字符串

                    # 提取函数名和参数
                    # \$ 匹配字面量 $，$ 在正则有特殊含义，必须转义, \{ 匹配字面量 {，{ 是分组符号，必须转义
                    # (\w+)	匹配函数名（字母/数字/下划线，如 get_extract_data）, (.*?)匹配括号内所有参数（支持带引号字符串，逗号分隔多参数）
                    match = re.match(r'\$\{(\w+)\((.*?)\)\}', variable_data)
                    if match:
                        func_name, func_params = match.groups()
                        # 先按逗号分割成参数列表，再去除每个参数前后空格
                        if func_params:
                            func_params = [p.strip() for p in func_params.split(",")]
                        else:
                            func_params = []

                        # 使用面向对象反射getattr调用函数
                        extract_data = getattr(self, func_name)(*func_params)

                        repl_text = str(extract_data)
                        # 直接普通字符串替换，避开正则re.sub的转义坑
                        yaml_data_str = yaml_data_str.replace(variable_data, repl_text)
                        print_log(f'解析yaml数据为{yaml_data_str}')
            return yaml_data_str
        # 字典：递归遍历每一个value
        elif isinstance(yaml_data, dict):
            new_dict = {}
            for k, v in yaml_data.items():
                new_dict[k] = self.yaml_variables(v)
            print_log(f'解析yaml数据为{new_dict}')
            return new_dict
        # 列表：递归遍历每一个元素
        elif isinstance(yaml_data, list):
            new_list = []
            for item in yaml_data:
                new_list.append(self.yaml_variables(item))
            print_log(f'解析yaml数据为{new_list}')
            return new_list
        # 数字、布尔、None直接原样返回
        else:
            return yaml_data


    # 解析yaml文件参数
    def variable_resolver(self,kwargs:dict):
        # 参数解析
        for kwargs_key in list(kwargs.keys()):
            kwargs[kwargs_key] = self.yaml_variables(yaml_data=kwargs[kwargs_key])

        # 通过files参数进行文件上传处理
        for args_key, args_value in kwargs.items():
            if args_key == "files":
                for file_key, file_value in args_value.items():
                    args_value[file_key] = open(file_value, "rb")
            print_log(f"请求{args_key}参数地址:{args_value}")
        return kwargs


    """ ============== 2.获取配置环境数据-地址 ================ """
    # 获取配置环境 url地址
    def env(self, key):
        if not hasattr(setting,
                       key):  # 判断对象是否拥有某个属性, setting：你导入的configs.setting,key：字符串变量名，例如 "phpwind_base_url",返回布尔值：True / False
            raise KeyError(f'setting.py文件不存在配置数据：{key}')
        return getattr(setting, key)  # 动态获取对象的属性值


    """ ============= 3.提取变量 ============= """
    # 提取值到全局变量 (提取数据到extract.yaml文件)
    def extract_yaml(self, extract_rule, resp_obj):
        # 后置 提取变量存至yaml
        if extract_rule is not None and isinstance(extract_rule, dict):
            extract_map = {}
            for save_key, rule_arr in extract_rule.items():
                extract_type, expr = rule_arr
                if extract_type == "json":
                    val_list = jsonpath.jsonpath(resp_obj.json(), expr)
                    if val_list:
                        extract_map[save_key] = val_list[0]
                elif extract_type == "text":
                    # 编译正则表达式
                    pattern = re.compile(expr)
                    # 在html全文搜索匹配
                    result = pattern.search(resp_obj.text)
                    if result:
                        extract_map[save_key] = result.group(1)
            if extract_map:
                write_yaml(extract_map, setting.extract_path)
                print_log(f'提取变量为{extract_map}')

    """ ============= 3.获取提取的变量 ============= """
    # 读取全局提取值的数据 (获取extract.yaml文件的数据)
    def get_extract_yaml(self,data_name, sub_data_name=None):
            extract_data = read_yaml(setting.extract_path)
            # 修复：空文件/无数据时返回None，不再直接取值
            if extract_data is None:
                return None
            if sub_data_name is None:
                return extract_data[data_name]
            else:
                return extract_data.get(data_name,{}).get(sub_data_name)  # 没有值就返回空字典, 有就再获取下级


    # 获取extract.yaml文件的 中间值，如token
    def get_extract_data(self,data_name,out_format=None):
        # out_format判断是否为数字类型，是 可以提取某一个或多个值，不是 则字典(上下层关系,下一个节点的值)，如cookie
        data = self.get_extract_yaml(data_name)
        # bool判断是数值 还是参数，正则(^开头，[+-]?可以正/负数，至少一个\d+数字，$结尾 匹配), 解析这个参数是否包含前面, r 是让 ‘\’ 不再做转义处理
        if out_format is not None and bool(re.compile(r'^[+-]?\d+$').match(str(out_format))):
            out_format = int(out_format)
            data_value = {
                out_format: self.seq_read(data,out_format),  # 按顺序取值（不为0，-1，-2时）
                0: random.choice(data),  # 从data列表随机选一个
                -1: ','.join(data),  # 列表所有元素用‘，’逗号 拼接成字符串
                -2: ','.join(data).split(',')  # 先逗号 拼接字符串，再按逗号 分割回列表（等价原列表，多用于统一格式）
            }
            data = data_value[out_format]
        else:
            data = self.get_extract_yaml(data_name,out_format)
        return data

    # 获取第二个参数不为0，-1，-2的情况， 按顺序取值
    def seq_read(self,data,randoms):   # randoms 传入数字的下标
        if randoms not in [0, -1, -2]:
            return data[randoms-1]  # 传1 → 取data[0]（第一个元素）
        else:
            return None



    """ ============ 4.断言 ============== """
    def data_validate(self,res_data,resp_obj):
        validate_rules = res_data.get("validate", {})  # 读取yaml中的预期校验规则
        # 获取响应数据，一次性解析，分开存储json对象与文本，全程不覆盖
        try:
            resp_json = resp_obj.json()
            resp_text = resp_obj.text
        except Exception:
            resp_json = None
            resp_text = resp_obj.text
        # 循环断言每一个校验字段
        for key, expect_val in validate_rules.items():
            if key == "contains" and key is not None:  # 判断字典内是否有该字段，全文文本匹配
                assert expect_val in resp_text, f"校验失败：响应JSON不存在字段【{expect_val}】\n实际完整响应为{resp_text}"
                print_log(f"字段存在校验通过：预期字段{expect_val}")
            elif key == "length":  # 【新增长度校验分支】
                target_key = expect_val.get("field")  # 需要校验长度的json字段名
                expect_len_rule = expect_val["len"]  # 预期长度规则（数字/>,<表达式）
                actual_data = resp_json.get(target_key)

                # 先判断字段是否存在
                assert actual_data is not None, f"长度校验失败：响应不存在字段 {target_key}"
                actual_len = len(actual_data)

                # 区分精确数字 / 区间表达式
                if isinstance(expect_len_rule, int):
                    # 精确长度匹配
                    assert actual_len == expect_len_rule, f"【长度校验】字段 {target_key} 失败：预期长度={expect_len_rule}，实际长度={actual_len}"
                    print_log(f"【长度校验】字段 {target_key} 通过：预期长度={expect_len_rule}，实际长度={actual_len}")
                else:
                    # 区间判断 >0 / <5 / >=2 / <=10
                    expr = f"{actual_len}{expect_len_rule}"
                    assert eval(expr), f"【长度区间校验】字段 {target_key} 失败：规则 {expr} 不成立，实际长度={actual_len}"
                    print_log(f"【长度区间校验】字段 {target_key} 通过：规则 {expr} 成立")
            else:
                # 等值断言
                actual_val = resp_json.get(key)
                assert actual_val == expect_val, f"校验{key}失败：预期{expect_val}，实际{actual_val}"
                print_log(f"校验{key}通过：预期{expect_val}，实际{actual_val}")


# if __name__ == "__main__":
#     t = Yamlvariablers()
#     a = t.env("wx_base_url")
#     print(a)

