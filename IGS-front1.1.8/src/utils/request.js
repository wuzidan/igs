import axios from "axios"
import querystring from "querystring"
let hostUrl = "http://localhost:5173"


const instance = axios.create({
    //baseUrl : hostUrl,
    baseURL: "http://localhost:8000",
    timeout: 5000   
})

// 拦截器 - 请求拦截器
instance.interceptors.request.use(
    config => {
        if (config.method === "post") {
            config.data = querystring.stringify(config.data)
        }
        return config
    },
    error => {
        return Promise.reject(error)
    }
)

// 拦截器 - 响应拦截器
instance.interceptors.response.use(
    response => {
        return response.status === 200 ? Promise.resolve(response) : Promise.reject(response)
    },
    error => {
        const { response } = error;
        let errorMsg = '请求失败，请稍后重试';
        
        if (response) {
            // 根据不同状态码处理错误
            switch (response.status) {
                case 400:
                    errorMsg = '请求参数错误';
                    break;
                case 401:
                    errorMsg = '未授权，请重新登录';
                    // 可以在这里添加跳转登录页的逻辑
                    // router.replace('/login');
                    break;
                case 403:
                    errorMsg = '权限不足，无法访问';
                    break;
                case 404:
                    errorMsg = '请求的资源不存在';
                    break;
                case 500:
                    errorMsg = '服务器内部错误';
                    break;
                case 502:
                    errorMsg = '网关错误';
                    break;
                case 504:
                    errorMsg = '请求超时';
                    break;
                default:
                    errorMsg = `请求错误，状态码：${response.status}`;
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
        // 如果需要UI展示错误，可以使用全局事件总线或状态管理
        // 例如：bus.emit('showError', errorMsg);
        
        return Promise.reject({
            message: errorMsg,
            originalError: error
        });
    }
)

export default instance;
