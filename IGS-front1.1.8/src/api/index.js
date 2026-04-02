import axios from "axios"
import path from "./path"

const api = {
    getHistory() {
        return axios.get(path.history)
    },
    getHomework() {
        return axios.get(path.quiz)
    },
    submitPracticeRecord(payload) {
        return axios.post(path.submitPracticeRecord, payload, {
            headers: {
                "Content-Type": "application/json"
            }
        })
    },
    getStructure() {
        return axios.get(path.structure)
    },
    getVisualization() {
        return axios.get(path.visualization)
    },
    getStudentinfo() {
        return axios.get(path.studentinfo)
    },
    putStudentinfo() {
        return axios.put(path.studentinfo)
    },
    getQuestion(page = 1, pageSize = 10) {
        return axios.get(path.quiz, {
            params: { page, page_size: pageSize }
        })
    },
    // 认知诊断API调用函数
    getCognitiveDiagnosis(userId) {
        return axios.get(path.cognitiveDiagnosis, {
            params: { user_id: userId }
        })
    },
    // 预测下一组题目API调用函数
    getPredictNextQuestions(userId) {
        return axios.get(path.predictNextQuestions, {
            params: { user_id: userId }
        })
    },
    // 获取知识图谱数据
    getKnowledgeGraph() {
        return axios.get(path.knowledgeGraph)
    },
    // 获取先修关系规则
    getPrerequisites(target) {
        return axios.get(path.prerequisites, {
            params: { target: target }
        })
    },
    // 获取题目统计数据
    getQuestionStats(user_id) {
        return axios.get("/question/stats/", {
            params: { user_id: user_id }
        })
    },
    // 获取LLM学习路径推荐
    getLearningRoute(payload) {
        return axios.post("http://localhost:8001/api/recommend_path/", payload, {
            headers: {
                "Content-Type": "application/json"
            }
        })
    },
}

export default api