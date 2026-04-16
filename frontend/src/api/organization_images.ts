import { httpClient } from './client'
import type { Message, OrganizationImageRead } from './types'

export class OrganizationImagesApi {
  /** GET /organizations/{org_id}/images */
  async list_organization_images(orgId: string): Promise<OrganizationImageRead[]> {
    const res = await httpClient.get<OrganizationImageRead[]>(
      `/organizations/${orgId}/images`,
    )
    return res.data
  }

  /** POST /organizations/{org_id}/images */
  async upload_organization_image(
    orgId: string,
    formData: FormData,
    onProgress?: (pct: number) => void,
  ): Promise<OrganizationImageRead> {
    const res = await httpClient.post<OrganizationImageRead>(
      `/organizations/${orgId}/images`,
      formData,
      {
        headers: { 'Content-Type': 'multipart/form-data' },
        onUploadProgress: onProgress
          ? (e) => {
              if (e.total) onProgress(Math.round((e.loaded * 100) / e.total))
            }
          : undefined,
      },
    )
    return res.data
  }

  /** DELETE /organizations/{org_id}/images/{image_id} */
  async delete_organization_image(orgId: string, imageId: string): Promise<Message> {
    const res = await httpClient.delete<Message>(
      `/organizations/${orgId}/images/${imageId}`,
    )
    return res.data
  }
}
