import axios from "axios"
import querystring from "querystring"
let hostUrl = "http://localhost:5173"


const instance = axios.create({
    //baseUrl : hostUrl,
    baseURL: "http://localhost:8000",
    timeout: 20000   
})

// 拦截器 - 请求拦截器
instance.interceptors.request.use(
    config => {
        console.log('发送请求:', {
            url: config.url,
            method: config.method,
            data: config.data,
            params: config.params
        });
        
        const token = window.localStorage ? window.localStorage.getItem("token") : null
        if (token) {
            config.headers = config.headers || {}
            config.headers.Authorization = `Token ${token}`
        }

        const method = (config.method || "").toLowerCase()
        const isFormData = typeof FormData !== "undefined" && config.data instanceof FormData
        const contentType = (() => {
            const headers = config.headers || {}
            return headers["Content-Type"] || headers["content-type"] || ""
        })()
        const isJson = typeof contentType === "string" && contentType.includes("application/json")

        if ((method === "post" || method === "put" || method === "patch") && !isFormData && !isJson) {
            config.data = querystring.stringify(config.data)
            config.headers = config.headers || {}
            if (!config.headers["Content-Type"]) {
                config.headers["Content-Type"] = "application/x-www-form-urlencoded"
            }
        }
        
        console.log('请求配置:', {
            headers: config.headers,
            contentType: config.headers["Content-Type"]
        });
        
        return config
    },
    error => {
        console.error('请求错误:', error);
        return Promise.reject(error)
    }
)

// 拦截器 - 响应拦截器
instance.interceptors.response.use(
    response => {
        // 接受所有2xx系列的成功状态码
        return response.status >= 200 && response.status < 300 ? Promise.resolve(response) : Promise.reject(response)
    },
    error => {
        const { response } = error;
        let errorMsg = '请求失败，请稍后重试';

        const serverMessage = (() => {
            const data = response && response.data
            if (!data) return null
            if (typeof data === 'string') return data
            if (typeof data === 'object') {
                if (data.error || data.detail || data.message) {
                    return data.error || data.detail || data.message
                }
                if (Array.isArray(data.non_field_errors) && data.non_field_errors.length > 0) {
                    return String(data.non_field_errors[0])
                }
                const firstFieldErrors = Object.values(data).find(value => Array.isArray(value) && value.length > 0)
                if (firstFieldErrors) {
                    return String(firstFieldErrors[0])
                }
                return null
            }
            return null
        })();
        
        if (response) {
            // 根据不同状态码处理错误
            switch (response.status) {
                case 400:
                    errorMsg = serverMessage || '请求参数错误';
                    break;
                case 401:
                    errorMsg = serverMessage || '未授权，请重新登录';
                    // 可以在这里添加跳转登录页的逻辑
                    // router.replace('/login');
                    break;
                case 403:
                    errorMsg = serverMessage || '权限不足，无法访问';
                    break;
                case 404:
                    errorMsg = serverMessage || '请求的资源不存在';
                    break;
                case 500:
                    errorMsg = serverMessage || '服务器内部错误';
                    break;
                case 502:
                    errorMsg = serverMessage || '网关错误';
                    break;
                case 504:
                    errorMsg = serverMessage || '请求超时';
                    break;
                default:
                    errorMsg = serverMessage || `请求错误，状态码：${response.status}`;
            }
        } else {
            // 无响应的情况（如网络断开）
            if (error.message.includes('timeout')) {
                errorMsg = '请求超时，请检查网络';
            } else if (error.message.includes('Network Error')) {
                errorMsg = '网络连接错误，请检查网络';
            }
        }
        
        // 可以在这里添加全局错误提示（如弹框提示）
        console.error('请求错误：', errorMsg);
        
        return Promise.reject({
            message: errorMsg,
            originalError: error
        });
    }
)

export default instance;
