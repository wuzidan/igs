import request from "../utils/request"
import axios from "axios"
import path from "./path"

const api = {
    getHistory() {
        return request.get(path.history)
    },
    getHomework() {
        return request.get(path.quiz)
    },
    submitPracticeRecord(payload) {
        return request.post(path.submitPracticeRecord, payload, {
            headers: {
                "Content-Type": "application/json"
            }
        })
    },
    getHomework() {
        return request.get(path.quiz)
    },
    submitPracticeRecord(payload) {
        return request.post(path.submitPracticeRecord, payload, {
            headers: {
                "Content-Type": "application/json"
            }
        })
    },
    getStructure() {
        return request.get(path.structure)
    },
    getVisualization() {
        return request.get(path.visualization)
    },
    getStudentinfo() {
        return request.get(path.studentinfo)
    },
    putStudentinfo() {
        return request.put(path.studentinfo)
    },
    getQuestion(page = 1, pageSize = 10) {
        return request.get(path.quiz, {
            params: { page, page_size: pageSize }
        })
    },
    // 认知诊断API调用函数
    getCognitiveDiagnosis(userId) {
        return request.get(path.cognitiveDiagnosis, {
            params: { user_id: userId }
        })
    },
    // 预测下一组题目API调用函数
    getPredictNextQuestions(userId) {
        return request.get(path.predictNextQuestions, {
            params: { user_id: userId }
        })
    },
    // 获取知识图谱数据
    getKnowledgeGraph() {
        return request.get(path.knowledgeGraph)
    },
    // 获取先修关系规则
    getPrerequisites(target) {
        return request.get(path.prerequisites, {
            params: { target: target }
        })
    },
    // 获取题目统计数据
    getQuestionStats(user_id) {
        return request.get("/question/stats/", {
            params: { user_id: user_id }
        })
    },
    // 获取LLM学习路径推荐
    getLearningRoute(payload) {
        return request.post("http://localhost:8001/api/recommend_path/", payload, {
            headers: {
                "Content-Type": "application/json"
            }
        })
    },
}

export default api