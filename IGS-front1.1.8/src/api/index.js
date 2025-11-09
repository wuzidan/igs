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
    putStudentinfo() {
        return axios.put(path.studentinfo)
    },
    getQuestion() {
        return axios.get(path.quiz)
    },
}

export default api