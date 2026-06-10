from __future__ import annotations

from enum import Enum
from typing import Optional

from pydantic import BaseModel, Field


# ============================================================
# Enums
# ============================================================

class ProjectStatusEnum(Enum):
    """
    `brief_generating`、`outline_ready`、`outline_confirmed`、`research_running`、`report_ready`
    """

    BRIEF_GENERATING = "brief_generating"
    OUTLINE_READY = "outline_ready"
    OUTLINE_CONFIRMED = "outline_confirmed"
    RESEARCH_RUNNING = "research_running"
    REPORT_READY = "report_ready"


class TaskStatusEnum(Enum):
    """
    `queued`、`running`、`succeeded`、`failed`
    """

    QUEUED = "queued"
    RUNNING = "running"
    SUCCEEDED = "succeeded"
    FAILED = "failed"


class TaskTypeEnum(Enum):
    """
    任务类型：
        生成大纲，
        修订大纲，
        生成报告
    """

    OUTLINE_GENERATION = "outline_generation"
    OUTLINE_REVISION = "outline_revision"
    REPORT_GENERATION = "report_generation"


class OutlineActionEnum(Enum):
    """大纲操作类型"""

    CONFIRM = "confirm"
    REVISE = "revise"


class SourceTypeEnum(Enum):
    """来源类型"""

    PUBLIC_WEB = "public_web"

class NextStepEnum(Enum):

    WAIT_FOR_OUTLINE="wait_for_outline"
    GENERATE_REPORT = "generate_report"


# ============================================================
# Shared / Nested models
# ============================================================

class TimeScope(BaseModel):
    type: str
    years: int


class OutlineNode(BaseModel):
    """大纲树节点"""

    node_id: str = Field(description="节点编号，如 1、1.1")
    title: str = Field(description="章节标题")
    question: str = Field(description="该章节要回答的核心问题")
    description: str = Field(description="章节描述与范围说明")
    children: list[OutlineNode] = Field(default_factory=list, description="子节点列表")


class Source(BaseModel):
    """信息来源"""

    source_id: str = Field(description="来源编号，如 S1")
    title: str = Field(description="来源标题")
    url: str = Field(description="来源链接")
    published_at: str = Field(description="发布日期")
    source_type: str = Field(description="来源类型，如 public_web")


# ============================================================
# Research - 创建研究项目
# ============================================================

class ResearchCreateRequest(BaseModel):
    topic: str = Field(description="当前研究的主题")
    research_goal: str = Field(description="研究目标")
    target_audience: str = Field(description="目标受众")
    region_scope: str = Field(description="地域范围")
    time_scope: TimeScope = Field(description="时间范围")


class ResearchCreateResponse(BaseModel):
    project_id: str = Field(description="项目编号")
    initial_task_id: str = Field(description="初始任务编号")
    initial_task_type: str = Field(description="初始任务类型")
    topic: str = Field(description="研究主题")
    status: str = Field(description="项目状态")
    next_step: str = Field(description="下一步操作")
    created_at: str = Field(description="创建时间")


# ============================================================
# Outline - 获取/确认大纲
# ============================================================

class GetOutlineResponse(BaseModel):
    """Get Outline 接口出参"""

    project_id: str = Field(description="项目编号")
    status: str = Field(description="项目状态")
    outline: list[OutlineNode] = Field(description="大纲树")


class SaveOutlineRequest(BaseModel):
    """保存已确认的大纲接口入参"""

    action: str = Field(description="操作类型：confirm 或 revise")
    revision_instruction: Optional[str] = Field(
        default=None, description="修订指令（action=revise 时必填）"
    )


class SaveOutlineResponse(BaseModel):
    """保存已确认的大纲接口出参"""

    project_id: str = Field(description="项目编号")
    status: str = Field(description="项目状态")
    revision_task_id: Optional[str] = Field(
        default=None, description="修订任务编号（action=revise 时返回）"
    )
    next_step: str = Field(description="下一步操作")


# ============================================================
# Report - 生成/获取报告
# ============================================================

class GenerateReportRequest(BaseModel):
    """提交报告生成任务入参"""

    user_instruction: str = Field(description="用户对报告风格的额外指令")


class GenerateReportResponse(BaseModel):
    """提交报告生成任务出参"""

    task_id: str = Field(description="任务编号")
    project_id: str = Field(description="项目编号")
    task_type: str = Field(description="任务类型")
    status: str = Field(description="任务状态")


# ============================================================
# Task - 查询任务状态
# ============================================================

class GetTaskStatusResponse(BaseModel):
    """查询任务状态出参"""

    task_id: str = Field(description="任务编号")
    project_id: str = Field(description="项目编号")
    task_type: str = Field(description="任务类型")
    status: str = Field(description="任务状态")
    message: str = Field(description="状态描述信息")
    created_at: str = Field(description="创建时间")
    updated_at: str = Field(description="更新时间")


# ============================================================
# Report - 获取最终报告
# ============================================================

class GetReportResponse(BaseModel):
    """获取最终报告出参"""

    project_id: str = Field(description="项目编号")
    report_id: str = Field(description="报告编号")
    version: int = Field(description="报告版本号")
    title: str = Field(description="报告标题")
    html: str = Field(description="报告正文 HTML")
    sources: list[Source] = Field(description="引用来源列表")
    created_at: str = Field(description="创建时间")
