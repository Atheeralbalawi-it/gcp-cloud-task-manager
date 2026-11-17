<!DOCTYPE html>
<html lang="ar" dir="rtl">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>إدارة المهام السحابية</title>
    <script src="https://cdn.tailwindcss.com"></script>
</head>
<body class="bg-gray-900 text-white min-h-screen flex flex-col items-center p-6">
    <div class="w-full max-w-md bg-gray-800 p-6 rounded-xl shadow-lg border border-gray-700">
        <h1 class="text-2xl font-bold mb-4 text-center text-blue-400">نظام إدارة المهام السحابي</h1>
        
        <!-- إضافة مهمة جديدة -->
        <div class="flex gap-2 mb-6">
            <input type="text" id="taskInput" placeholder="أدخل مهمة جديدة..." class="flex-1 bg-gray-900 border border-gray-700 rounded-lg px-4 py-2 text-white focus:outline-none focus:border-blue-500">
            <button onclick="addTask()" class="bg-blue-600 hover:bg-blue-500 px-4 py-2 rounded-lg font-bold transition">إضافة</button>
        </div>

        <!-- قائمة المهام -->
        <ul id="taskList" class="space-y-3">
            <!-- سيتم تعبئة المهام هنا تلقائياً -->
        </ul>
    </div>

    <script>
        // استبدل هذا الرابط برابط خدمة Render الخاصة بك لاحقاً
        const API_URL = "http://127.0.0.1:5000"; 

        async function fetchTasks() {
            try {
                const response = await fetch(${API_URL}/api/tasks);
                const tasks = await response.json();
                const list = document.getElementById('taskList');
                list.innerHTML = '';
                tasks.forEach(task => {
                    list.innerHTML += <li class="bg-gray-700 p-3 rounded-lg flex justify-between items-center"><span>${task.title}</span><span class="text-xs ${task.done ? 'text-green-400' : 'text-yellow-400'}">${task.done ? 'منجزة' : 'قيد العمل'}</span></li>;
                });
            } catch (error) {
                console.error("خطأ في جلب المهام:", error);
            }
        }

        async function addTask() {
            const input = document.getElementById('taskInput');
            if (!input.value) return;
            await fetch(${API_URL}/api/tasks, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ title: input.value })
            });
            input.value = '';
            fetchTasks();
        }

        fetchTasks();
    </script>
</body>
</html>
