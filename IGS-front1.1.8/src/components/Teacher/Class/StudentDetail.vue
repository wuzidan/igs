<template>
    <div class="student-detail-page">
        <div class="page-header">
            <div>
                <h2>学生详情</h2>
                <p>查看学生基础信息与知识点掌握情况</p>
            </div>
            <el-button @click="goBack">返回学生列表</el-button>
        </div>

        <el-card class="section-card" v-loading="loadingStudent">
            <template #header>
                <div class="card-header">基础信息</div>
            </template>
            <div class="info-grid">
                <div><span class="label">学生ID：</span>{{ student.studentId || studentId }}</div>
                <div><span class="label">姓名：</span>{{ student.name || '-' }}</div>
                <div><span class="label">学号：</span>{{ student.studentId || '-' }}</div>
                <div><span class="label">班级：</span>{{ student.class_name || '-' }}</div>
            </div>
        </el-card>

        <el-card class="section-card" v-loading="loadingMastery">
            <template #header>
                <div class="card-header">知识点掌握度</div>
            </template>

            <div v-if="Object.keys(diagnosisInfo).length" class="diagnosis-summary">
                <div class="diagnosis-badges">
                    <span class="diagnosis-badge" :class="confidenceClass">
                        置信等级：{{ confidenceLabel }}
                    </span>
                    <span class="diagnosis-badge" :class="formalDiagnosisClass">
                        {{ diagnosisInfo.formal_diagnosis ? '正式诊断' : '参考诊断' }}
                    </span>
                    <span v-if="diagnosisInfo.used_model_inference" class="diagnosis-badge info">
                        模型推理
                    </span>
                    <span v-else class="diagnosis-badge neutral">
                        非模型直推
                    </span>
                </div>

                <div class="diagnosis-meta-grid">
                    <div><span class="label">交互记录：</span>{{ diagnosisInfo.total_interactions || 0 }} 条</div>
                    <div><span class="label">有效记录：</span>{{ diagnosisInfo.valid_interactions || 0 }} 条</div>
                    <div><span class="label">最少样本：</span>{{ diagnosisInfo.min_required_interactions || '-' }} 条</div>
                    <div><span class="label">诊断模式：</span>{{ diagnosisInfo.model_status || '-' }}</div>
                </div>

                <div v-if="diagnosisInfo.low_confidence" class="diagnosis-alert warning">
                    当前诊断为低置信度结果，建议继续练习后再查看。
                </div>
                <div v-if="diagnosisInfo.stability_warning" class="diagnosis-alert danger">
                    {{ diagnosisInfo.stability_warning }}
                </div>
                <div
                    v-if="diagnosisMessages.length"
                    class="diagnosis-messages"
                >
                    <div v-for="(item, idx) in diagnosisMessages" :key="idx" class="diagnosis-message-item">
                        {{ item }}
                    </div>
                </div>
            </div>

            <div v-if="skills.length" class="skills-list">
                <div v-for="skill in skills" :key="`${skill.topicId || skill.name}`" class="skill-item">
                    <div class="skill-row">
                        <span class="skill-name">{{ skill.name }}</span>
                        <span class="skill-level">{{ skill.level }}%</span>
                    </div>
                    <el-progress
                        :percentage="Number(skill.level || 0)"
                        :stroke-width="12"
                        :color="skill.color || '#409eff'"
                    />
                </div>
            </div>
            <el-empty v-else description="暂无知识点掌握数据" />

            <div v-if="recommendations.length" class="recommendations">
                <h4>学习建议</h4>
                <ul>
                    <li v-for="(item, idx) in recommendations" :key="idx">{{ item }}</li>
                </ul>
            </div>
        </el-card>
    </div>
</template>

<script setup>
import { computed, onMounted, ref } from 'vue';
import { useRoute, useRouter } from 'vue-router';
import { ElMessage } from 'element-plus';
import request from '../../../utils/request';

const route = useRoute();
const router = useRouter();

const loadingStudent = ref(false);
const loadingMastery = ref(false);

const student = ref({});
const skills = ref([]);
const recommendations = ref([]);
const diagnosisInfo = ref({});

const studentId = computed(() => String(route.params.studentId || ''));
const classId = computed(() => String(route.query.classId || ''));
const diagnosisMessages = computed(() => {
    const messages = diagnosisInfo.value?.diagnosis_messages;
    return Array.isArray(messages) ? messages : [];
});
const confidenceLabel = computed(() => {
    const level = diagnosisInfo.value?.confidence_level;
    if (level === 'high') return '高';
    if (level === 'medium') return '中';
    if (level === 'low') return '低';
    return '未知';
});
const confidenceClass = computed(() => {
    const level = diagnosisInfo.value?.confidence_level;
    if (level === 'high') return 'success';
    if (level === 'medium') return 'warning';
    if (level === 'low') return 'danger';
    return 'neutral';
});
const formalDiagnosisClass = computed(() => (
    diagnosisInfo.value?.formal_diagnosis ? 'success' : 'warning'
));

const goBack = () => {
    if (classId.value) {
        router.push({ name: 'class-info', query: { classId: classId.value } });
        return;
    }
    router.push({ name: 'class-info' });
};

const fetchStudentDetail = async () => {
    if (!studentId.value || !classId.value) {
        student.value = { id: studentId.value };
        return;
    }

    loadingStudent.value = true;
    try {
        const resp = await request.get(`/classInfo/classes/${classId.value}/students/${studentId.value}/`);
        student.value = resp?.data || { id: studentId.value };
    } catch (e) {
        student.value = { id: studentId.value };
    } finally {
        loadingStudent.value = false;
    }
};

const fetchMastery = async () => {
    const actualStudentId = student.value.studentId || studentId.value;
    if (!actualStudentId) {
        return;
    }

    loadingMastery.value = true;
    try {
        const resp = await request.get(`/teacher/student-knowledge-mastery/?student_id=${actualStudentId}`);
        const data = resp?.data;
        if (data?.status === 'success') {
            skills.value = Array.isArray(data.skills) ? data.skills : [];
            recommendations.value = Array.isArray(data.recommendations) ? data.recommendations : [];
            diagnosisInfo.value = data.diagnosis_info || {};
            if (!student.value?.name && data.student_name) {
                student.value = {
                    ...student.value,
                    studentId: actualStudentId,
                    name: data.student_name,
                };
            }
            return;
        }
        skills.value = [];
        recommendations.value = [];
        diagnosisInfo.value = {};
    } catch (e) {
        skills.value = [];
        recommendations.value = [];
        diagnosisInfo.value = {};
        ElMessage.error('获取学生知识点掌握度失败');
    } finally {
        loadingMastery.value = false;
    }
};

onMounted(async () => {
    await fetchStudentDetail();
    await fetchMastery();
});
</script>

<style scoped>
.student-detail-page {
    padding: 0;
}

.page-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 16px;
}

.page-header h2 {
    margin: 0;
    color: #1e3a8a;
}

.page-header p {
    margin: 6px 0 0;
    color: #64748b;
}

.section-card {
    margin-bottom: 16px;
}

.diagnosis-summary {
    margin-bottom: 18px;
    padding: 14px;
    border-radius: 12px;
    background: linear-gradient(135deg, #f8fbff 0%, #eef6ff 100%);
    border: 1px solid #dbeafe;
}

.diagnosis-badges {
    display: flex;
    flex-wrap: wrap;
    gap: 10px;
    margin-bottom: 12px;
}

.diagnosis-badge {
    display: inline-flex;
    align-items: center;
    padding: 6px 12px;
    border-radius: 999px;
    font-size: 13px;
    font-weight: 600;
}

.diagnosis-badge.success {
    background: #dcfce7;
    color: #166534;
}

.diagnosis-badge.warning {
    background: #fef3c7;
    color: #92400e;
}

.diagnosis-badge.danger {
    background: #fee2e2;
    color: #991b1b;
}

.diagnosis-badge.info {
    background: #dbeafe;
    color: #1d4ed8;
}

.diagnosis-badge.neutral {
    background: #e5e7eb;
    color: #374151;
}

.diagnosis-meta-grid {
    display: grid;
    grid-template-columns: repeat(2, minmax(0, 1fr));
    gap: 10px 14px;
    margin-bottom: 12px;
    color: #334155;
}

.diagnosis-alert {
    padding: 10px 12px;
    border-radius: 10px;
    margin-top: 10px;
    font-size: 14px;
}

.diagnosis-alert.warning {
    background: #fff7ed;
    color: #9a3412;
}

.diagnosis-alert.danger {
    background: #fef2f2;
    color: #b91c1c;
}

.diagnosis-messages {
    margin-top: 10px;
    display: grid;
    gap: 8px;
}

.diagnosis-message-item {
    color: #475569;
    font-size: 14px;
}

.card-header {
    font-weight: 600;
    color: #1f2937;
}

.info-grid {
    display: grid;
    grid-template-columns: repeat(2, minmax(0, 1fr));
    gap: 12px;
    color: #334155;
}

.label {
    color: #64748b;
}

.skills-list {
    display: grid;
    gap: 14px;
}

.skill-row {
    display: flex;
    justify-content: space-between;
    margin-bottom: 6px;
}

.skill-name {
    color: #1f2937;
}

.skill-level {
    color: #334155;
}

.recommendations {
    margin-top: 16px;
}

.recommendations h4 {
    margin: 0 0 8px;
    color: #1f2937;
}

.recommendations ul {
    margin: 0;
    padding-left: 18px;
    color: #475569;
}

@media (max-width: 768px) {
    .info-grid {
        grid-template-columns: 1fr;
    }

    .diagnosis-meta-grid {
        grid-template-columns: 1fr;
    }

    .page-header {
        flex-direction: column;
        align-items: flex-start;
        gap: 10px;
    }
}
</style>
