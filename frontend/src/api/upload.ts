import { httpClient } from './client'
import type { Message, UploadResponse } from './types'

export class UploadApi {
  /** POST /upload/image */
  async upload_image(
    formData: FormData,
    onProgress?: (pct: number) => void,
  ): Promise<UploadResponse> {
    const res = await httpClient.post<UploadResponse>('/upload/image', formData, {
      headers: { 'Content-Type': 'multipart/form-data' },
      onUploadProgress: onProgress
        ? (e) => {
            if (e.total) onProgress(Math.round((e.loaded * 100) / e.total))
          }
        : undefined,
    })
    return res.data
  }

  /** POST /upload/video */
  async upload_video(
    formData: FormData,
    onProgress?: (pct: number) => void,
  ): Promise<UploadResponse> {
    const res = await httpClient.post<UploadResponse>('/upload/video', formData, {
      headers: { 'Content-Type': 'multipart/form-data' },
      onUploadProgress: onProgress
        ? (e) => {
            if (e.total) onProgress(Math.round((e.loaded * 100) / e.total))
          }
        : undefined,
    })
    return res.data
  }

  /** DELETE /upload/image */
  async delete_image(filename: string): Promise<Message> {
    const res = await httpClient.delete<Message>('/upload/image', { params: { filename } })
    return res.data
  }
}
