# 微信公众号小程序接口测试框架
测试 创建项目（仅用于测试）
# 目录结构
<img width="848" height="423" alt="项目结构" src="https://github.com/user-attachments/assets/3bb8f71c-6ca2-4ec8-ae2e-fa4fd839a3a0" />

# 依赖说明
这里运用的CentOS7，考虑到allure报告，urllib3 v2 版本要求 OpenSSL 1.1.1+，但你的容器环境（很可能是 CentOS 7 或类似）的 OpenSSL 版本为 1.0.2k，导致导入失败
urllib3<2.0
requests>=2.28.0

# 附带 测试用例
附带 登录、内容编辑、文件上传的测试用例
