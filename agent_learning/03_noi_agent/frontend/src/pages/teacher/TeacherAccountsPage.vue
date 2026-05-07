<script setup>
import { computed, onMounted, reactive, ref } from 'vue';

import {
  createTeacherStudent,
  createTeacherStudentsBulk,
  getTeacherStudents,
  resetTeacherStudentPassword,
  updateTeacherStudentStatus,
} from '@/services/api';
import { useAuthStore } from '@/stores/auth';

const auth = useAuthStore();
const loading = ref(false);
const savingAccount = ref(false);
const savingBatch = ref(false);
const error = ref('');
const accountMessage = ref('');
const batchAccountText = ref('');
const batchResult = ref(null);
const students = ref([]);
const createdAccount = ref(null);

const accountForm = reactive({
  display_name: '',
  user_id: '',
  password: '',
});

const activeStudents = computed(() => students.value.filter((item) => item.active !== false));

function splitBatchLine(line) {
  if (line.includes('\t')) return line.split('\t');
  return line.split(',');
}

function parseBatchAccountRows() {
  const lines = batchAccountText.value
    .split(/\r?\n/)
    .map((line) => line.trim())
    .filter(Boolean);
  return lines
    .map((line, index) => {
      const cells = splitBatchLine(line).map((cell) => cell.trim());
      const first = (cells[0] || '').toLowerCase();
      if (index === 0 && ['display_name', '姓名', '显示姓名', 'name'].includes(first)) {
        return null;
      }
      return {
        row_index: index + 1,
        display_name: cells[0] || '',
        user_id: cells[1] || '',
        password: cells[2] || '',
      };
    })
    .filter(Boolean);
}

async function loadStudents() {
  loading.value = true;
  error.value = '';
  try {
    const result = await getTeacherStudents(auth.token);
    students.value = result.students || [];
  } catch (err) {
    error.value = err.message || '加载学生账号失败';
  } finally {
    loading.value = false;
  }
}

async function submitAccountForm() {
  if (!accountForm.display_name.trim()) {
    accountMessage.value = '请先填写显示姓名。';
    return;
  }
  savingAccount.value = true;
  error.value = '';
  accountMessage.value = '';
  createdAccount.value = null;
  try {
    const result = await createTeacherStudent(auth.token, {
      display_name: accountForm.display_name.trim(),
      user_id: accountForm.user_id.trim(),
      password: accountForm.password.trim(),
    });
    createdAccount.value = result.student;
    accountMessage.value = '学生账号已创建，请把初始密码及时发给学生。';
    accountForm.display_name = '';
    accountForm.user_id = '';
    accountForm.password = '';
    await loadStudents();
  } catch (err) {
    accountMessage.value = err.message || '创建学生账号失败';
  } finally {
    savingAccount.value = false;
  }
}

async function submitBatchAccounts() {
  const rows = parseBatchAccountRows();
  if (rows.length === 0) {
    accountMessage.value = '请先粘贴学生名单。';
    return;
  }
  savingBatch.value = true;
  error.value = '';
  accountMessage.value = '';
  batchResult.value = null;
  try {
    const result = await createTeacherStudentsBulk(auth.token, { rows });
    batchResult.value = result;
    accountMessage.value = `批量创建完成：成功 ${result.success_rows?.length || 0} 行，失败 ${result.failed_rows?.length || 0} 行。`;
    if ((result.failed_rows || []).length === 0) {
      batchAccountText.value = '';
    }
    await loadStudents();
  } catch (err) {
    accountMessage.value = err.message || '批量创建学生账号失败';
  } finally {
    savingBatch.value = false;
  }
}

async function resetPassword(student) {
  accountMessage.value = '';
  createdAccount.value = null;
  try {
    const result = await resetTeacherStudentPassword(auth.token, student.user_id, {});
    createdAccount.value = result.student;
    accountMessage.value = '密码已重置，请把新密码及时发给学生。';
    await loadStudents();
  } catch (err) {
    accountMessage.value = err.message || '重置密码失败';
  }
}

async function toggleStudentActive(student) {
  accountMessage.value = '';
  try {
    await updateTeacherStudentStatus(auth.token, student.user_id, student.active === false);
    accountMessage.value = student.active === false ? '学生账号已启用。' : '学生账号已停用。';
    await loadStudents();
  } catch (err) {
    accountMessage.value = err.message || '更新账号状态失败';
  }
}

onMounted(loadStudents);
</script>

<template>
  <div class="space-y-6">
    <section class="grid gap-4 lg:grid-cols-3">
      <article class="metric-tile">
        <p class="text-sm text-slate-400">学生账号</p>
        <p class="mt-2 text-2xl font-semibold text-slate-900">{{ students.length }}</p>
      </article>
      <article class="metric-tile">
        <p class="text-sm text-slate-400">可登录账号</p>
        <p class="mt-2 text-2xl font-semibold text-slate-900">{{ activeStudents.length }}</p>
      </article>
      <article class="metric-tile">
        <p class="text-sm text-slate-400">已停用账号</p>
        <p class="mt-2 text-2xl font-semibold text-slate-900">{{ students.length - activeStudents.length }}</p>
      </article>
    </section>

    <section class="panel">
      <div class="mb-5 flex flex-col gap-3 md:flex-row md:items-start md:justify-between">
        <div>
          <p class="section-eyebrow text-cyan-700">账号</p>
          <h3 class="mt-2 font-display text-2xl font-bold text-slate-900">创建学生账号</h3>
          <p class="mt-2 text-sm leading-6 text-slate-500">只在创建或重置时显示明文密码，请及时记录给学生。</p>
        </div>
        <button class="button-secondary" type="button" @click="loadStudents">刷新</button>
      </div>

      <form class="grid gap-4 lg:grid-cols-[1fr_1fr_1fr_auto]" @submit.prevent="submitAccountForm">
        <label class="block">
          <span class="text-sm font-semibold text-slate-700">显示姓名</span>
          <input
            v-model="accountForm.display_name"
            class="mt-2 w-full rounded-[18px] border border-slate-200 bg-white px-4 py-3 text-sm outline-none focus:border-cyan-400"
            placeholder="例如：张三"
          />
        </label>
        <label class="block">
          <span class="text-sm font-semibold text-slate-700">登录账号</span>
          <input
            v-model="accountForm.user_id"
            class="mt-2 w-full rounded-[18px] border border-slate-200 bg-white px-4 py-3 text-sm outline-none focus:border-cyan-400"
            placeholder="可留空自动生成"
          />
        </label>
        <label class="block">
          <span class="text-sm font-semibold text-slate-700">初始密码</span>
          <input
            v-model="accountForm.password"
            class="mt-2 w-full rounded-[18px] border border-slate-200 bg-white px-4 py-3 text-sm outline-none focus:border-cyan-400"
            placeholder="可留空自动生成"
          />
        </label>
        <div class="flex items-end">
          <button class="button-primary w-full" type="submit" :disabled="savingAccount">
            {{ savingAccount ? '创建中...' : '创建账号' }}
          </button>
        </div>
      </form>

      <div v-if="accountMessage" class="mt-4 rounded-[18px] border border-cyan-100 bg-cyan-50 px-4 py-3 text-sm font-medium text-cyan-800">
        {{ accountMessage }}
      </div>
      <div v-if="createdAccount" class="mt-4 rounded-[18px] border border-emerald-100 bg-emerald-50 px-4 py-3 text-sm text-emerald-800">
        <p class="font-semibold">账号：{{ createdAccount.user_id }}</p>
        <p class="mt-1">姓名：{{ createdAccount.display_name }}</p>
        <p class="mt-1">密码：{{ createdAccount.password }}</p>
      </div>
    </section>

    <section class="panel">
      <div class="mb-5 flex flex-col gap-3 md:flex-row md:items-start md:justify-between">
        <div>
          <p class="section-eyebrow text-cyan-700">批量导入</p>
          <h3 class="mt-2 font-display text-2xl font-bold text-slate-900">批量创建账号</h3>
          <p class="mt-2 text-sm leading-6 text-slate-500">
            粘贴表格或 CSV，每行按“显示姓名、登录账号、初始密码”排列；账号和密码可以留空自动生成。
          </p>
        </div>
        <button class="button-primary px-4 py-2 text-sm" type="button" :disabled="savingBatch" @click="submitBatchAccounts">
          {{ savingBatch ? '批量创建中...' : '批量创建' }}
        </button>
      </div>
      <textarea
        v-model="batchAccountText"
        class="min-h-36 w-full rounded-[18px] border border-cyan-100 bg-white px-4 py-3 text-sm outline-none focus:border-cyan-400"
        placeholder="粘贴表格，例如：
张三,stu001,pass123
李四,stu002,
王五,,"
      />
      <div v-if="batchResult" class="mt-4 grid gap-4 lg:grid-cols-2">
        <div class="rounded-[18px] border border-emerald-100 bg-emerald-50 p-4 text-sm text-emerald-800">
          <p class="font-semibold">成功创建 {{ batchResult.success_rows?.length || 0 }} 个账号</p>
          <div v-for="row in batchResult.success_rows || []" :key="`ok-${row.row_index}`" class="mt-2">
            第 {{ row.row_index }} 行：{{ row.student.display_name }} / {{ row.student.user_id }} / {{ row.student.password }}
          </div>
        </div>
        <div class="rounded-[18px] border border-rose-100 bg-rose-50 p-4 text-sm text-rose-800">
          <p class="font-semibold">失败 {{ batchResult.failed_rows?.length || 0 }} 行</p>
          <div v-for="row in batchResult.failed_rows || []" :key="`fail-${row.row_index}`" class="mt-2">
            第 {{ row.row_index }} 行：{{ row.error_message }}
          </div>
          <p v-if="(batchResult.failed_rows || []).length === 0" class="mt-2">没有失败行。</p>
        </div>
      </div>
    </section>

    <section class="panel">
      <div class="mb-4 flex items-center justify-between">
        <div>
          <p class="section-eyebrow text-cyan-700">账号列表</p>
          <h3 class="mt-2 font-display text-2xl font-bold text-slate-900">学生账号状态</h3>
        </div>
      </div>
      <p v-if="loading" class="text-sm text-slate-500">正在加载学生账号...</p>
      <p v-else-if="error" class="rounded-2xl bg-rose-50 px-4 py-3 text-sm font-medium text-rose-700">{{ error }}</p>
      <div v-else class="overflow-hidden rounded-[22px] border border-slate-100 bg-white">
        <table class="w-full text-left text-sm">
          <thead class="bg-slate-50 text-slate-500">
            <tr>
              <th class="px-4 py-3 font-semibold">显示姓名</th>
              <th class="px-4 py-3 font-semibold">登录账号</th>
              <th class="px-4 py-3 font-semibold">状态</th>
              <th class="px-4 py-3 font-semibold">操作</th>
            </tr>
          </thead>
          <tbody class="divide-y divide-slate-100">
            <tr v-for="student in students" :key="student.user_id">
              <td class="px-4 py-3 font-medium text-slate-900">{{ student.display_name || student.user_id }}</td>
              <td class="px-4 py-3 text-slate-600">{{ student.user_id }}</td>
              <td class="px-4 py-3">
                <span :class="['tag-pill', student.active === false ? 'bg-slate-100 text-slate-500' : 'bg-emerald-50 text-emerald-700']">
                  {{ student.active === false ? '已停用' : '可登录' }}
                </span>
              </td>
              <td class="px-4 py-3">
                <div class="flex flex-wrap gap-2">
                  <button class="button-secondary px-3 py-2 text-xs" type="button" @click="resetPassword(student)">重置密码</button>
                  <button class="button-secondary px-3 py-2 text-xs" type="button" @click="toggleStudentActive(student)">
                    {{ student.active === false ? '启用' : '停用' }}
                  </button>
                </div>
              </td>
            </tr>
          </tbody>
        </table>
        <div v-if="students.length === 0" class="border-t border-dashed border-slate-200 bg-slate-50 p-5 text-sm text-slate-500">
          暂无学生账号，可以先在上方创建一个。
        </div>
      </div>
    </section>
  </div>
</template>
