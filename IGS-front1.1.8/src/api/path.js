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
}

export default base