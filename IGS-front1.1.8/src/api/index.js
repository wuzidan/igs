import axios from "../utils/request"
import path from "./path"

const api = {
    getHistory() {
        return axios.get(path.history)
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
    putStudentinfo(saveData) {
        return axios.put(path.studentinfo, saveData)
    },
    getQuestion() {
        return axios.get(path.quiz)
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
    getTeacherInfo() {
        return axios.get(path.teacherInfo)
    }
}

export default api