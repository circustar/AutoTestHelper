create table flow.t_test_instance
(
    TEST_INSTANCE_ID     int auto_increment comment '测试实例ID'
        primary key,
    TEST_INSTANCE_NAME    varchar(100)  not null comment '测试实例名称',
    TEST_CASE_ID     int          not null comment '测试用例ID',
    TEST_CASE_NAME   varchar(100)  not null comment '测试用例名称',
    TEST_PARAMS json          null comment '测试用例参数',
    IS_DELETED       varchar(1)    null comment '逻辑删除标记；0:未删除，1：已删除',
    CREATE_TIME      datetime      null comment '创建时间',
    CREATE_USER      varchar(100)  null comment '创建人',
    UPDATE_TIME      datetime      null comment '修改时间',
    UPDATE_USER      varchar(100)  null comment '修改人'
)
    comment '测试用例';


create table flow.t_test_case
(
    TEST_CASE_ID     int auto_increment comment '测试用例模板ID'
        primary key,
    TEST_CASE_NAME   varchar(100)  not null comment '测试用例名称',
    TEST_CASE_USAGE  varchar(1000) null comment '测试用例用途',
    TEST_PARAMS json          null comment '测试用例模板参数',
    IS_DELETED       varchar(1)    null comment '逻辑删除标记；0:未删除，1：已删除',
    CREATE_TIME      datetime      null comment '创建时间',
    CREATE_USER      varchar(100)  null comment '创建人',
    UPDATE_TIME      datetime      null comment '修改时间',
    UPDATE_USER      varchar(100)  null comment '修改人'
)
    comment '测试用例模板';

create table flow.t_test_case_result
(
    TEST_CASE_RESULT_ID       int auto_increment comment '测试用例结果主键'
        primary key,
    TEST_CASE_ID              int          not null comment '测试用例主键',
    TEST_INSTANCE_ID          int         comment '测试实例主键',
    TEST_PARAMS json          null comment '测试用例参数',
    RESULT_OK                 varchar(1)   null comment '测试结果；0:未通过，1：通过',
    ERROR_TEST_CASE_STEP_ID   int          null comment '测试用例报错步骤ID',
    ERROR_TEST_CASE_STEP_NAME varchar(100) null comment '测试用例报错步骤名',
    ERROR_INFO                varchar(500) null comment '报错内容',
    ERROR_SCREEN_SHOT_PATH    varchar(512) null comment '报错时屏幕截图地址',
    IS_DELETED                varchar(1)   null comment '逻辑删除标记；0:未删除，1：已删除',
    CREATE_TIME               datetime     null comment '创建时间',
    CREATE_USER               varchar(100) null comment '创建人',
    UPDATE_TIME               datetime     null comment '修改时间',
    UPDATE_USER               varchar(100) null comment '修改人'
)
    comment '测试结果';

create table flow.t_test_case_step
(
    TEST_CASE_STEP_ID      int auto_increment comment '测试用例步骤ID'
        primary key,
    TEST_CASE_ID           int          not null comment '测试用例主键',
    TEST_CASE_STEP_NAME    varchar(100) not null comment '测试用例步骤名',
    STEP_ORDER             int          null comment '测试顺序',
    TEST_CASE_STEP_CONTENT varchar(500) null comment '测试用例步骤内容',
    TEST_CASE_STEP_EXPECT  varchar(500) null comment '期望结果',
    IS_DELETED             varchar(1)   null comment '逻辑删除标记；0:未删除，1：已删除',
    CREATE_TIME            datetime     null comment '创建时间',
    CREATE_USER            varchar(100) null comment '创建人',
    UPDATE_TIME            datetime     null comment '修改时间',
    UPDATE_USER            varchar(100) null comment '修改人'
)
    comment '测试用例步骤';

