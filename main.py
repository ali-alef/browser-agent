import asyncio
import sys

import browser_use

import copilot_chat_model
import task_manager


async def run_one_task(task: task_manager.TaskRecord) -> None:
    task.status = "running"
    task.failure_category = None
    task.final_output = ""
    task.step_trace = []

    try:
        prompt = task.prompt.strip()
        agent = browser_use.Agent(
            task=prompt,
            llm=copilot_chat_model.ChatCopilotCLI(model=task.model),
            task_id=str(task.id),
            browser=browser_use.Browser(proxy=browser_use.browser.ProxySettings(server="socks5://localhost:2080"))
        )
        history = await agent.run()

        task.step_trace = history.model_dump().get("history", [])
        task.final_output = history.final_result() or ""

        # TODO: Find a better way to clusterize the failure reasons and categories.
        if history.is_successful() and history.is_done():
            task.status = "completed"
        elif not history.is_successful():
            task.status = "failed"
            task.failure_category = "agent_unsuccessful"
            task.status = "completed"
        else:
            task.status = "failed"
            task.failure_category = "agent_incomplete"

    except Exception as exc:
        task.status = "failed"
        task.failure_category = type(exc).__name__
        task.final_output = str(exc)


async def main() -> None:
    tasks = task_manager.load_tasks()
    if len(sys.argv) > 1 and sys.argv[1].isdigit():
        for task in tasks:
            if task.id == int(sys.argv[1]):
                print(f"Running task {task.id}...")
                await run_one_task(task)
                task_manager.save_tasks(tasks)
                print(f"Task {task.id} -> {task.status}")
        return

    print("No task ID was provided running all pending tasks.")
    pending = [task for task in tasks if task.status == "pending"]

    if not pending:
        print("No pending tasks found.")
        return

    for task in pending:
        print(f"Running task {task.id}...")
        await run_one_task(task)
        task_manager.save_tasks(tasks)
        print(f"Task {task.id} -> {task.status}")

asyncio.run(main())
