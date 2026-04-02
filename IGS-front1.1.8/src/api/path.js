const base = {
    //baseURL: "https://mock.presstime.cn/mock/689a0e8c09b6bb83e73c1fca/IGSFRONT",
    baseURL: "http://localhost:8000",
    history: "/historyRecord/getHistoryRecord/",
    submitPracticeRecord: "/historyRecord/submitPracticeRecord/",
    structure: "/knowledge/structure/",
    visualization: "/visualization/display/",
    studentinfo: "/student/studentInfo/",
    quiz: "/question/question/", // 修改为正确的后端配置路径
    cognitiveDiagnosis: "/model/cognitiveDiagnosis/", // 认知诊断API路径
    predictNextQuestions: "/model/predictNextQuestions/", // 预测下一组题目API路径
    knowledgeGraph: "/graphs/neo4j/graph/", // 知识图谱数据API路径
    prerequisites: "/graphs/neo4j/prerequisites/", // 先修关系规则API路径
    questionStats: "/question/stats/", // 题目统计数据API路径
    recommendPath: "/api/recommend_path/", // LLM学习路径推荐API路径
}

export default base