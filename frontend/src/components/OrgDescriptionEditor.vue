<template>
  <div class="org-description-editor">
    <!-- Toolbar -->
    <div class="flex flex-wrap items-center gap-2 mb-2 p-2 bg-gray-50 rounded-t-lg border border-b-0 border-gray-200">
      <button type="button" @click="insert('**', '**')" title="Gras" class="toolbar-btn">
        <strong>B</strong>
      </button>
      <button type="button" @click="insert('*', '*')" title="Italique" class="toolbar-btn italic">
        I
      </button>
      <button type="button" @click="insertListItem()" title="Liste" class="toolbar-btn">
        •—
      </button>
      <button type="button" @click="insertHr()" title="Séparateur" class="toolbar-btn">
        —
      </button>

      <div class="w-px h-5 bg-gray-300 mx-1"></div>

      <!-- Insert member -->
      <div class="relative" ref="memberDropdownRef">
        <button type="button" @click="showMemberDropdown = !showMemberDropdown"
          class="toolbar-btn flex items-center gap-1" title="Insérer un membre">
          <UserCircleIcon class="h-4 w-4" />
          <span class="text-xs">Membre</span>
        </button>
        <div v-if="showMemberDropdown"
          class="absolute left-0 top-full mt-1 z-50 bg-white shadow-lg rounded-lg border border-gray-200 w-64 max-h-64 overflow-y-auto">
          <div class="p-2 border-b border-gray-100">
            <input v-model="memberSearch" type="text" placeholder="Rechercher..."
              class="block w-full text-sm rounded border border-gray-200 px-2 py-1 focus:outline-none focus:ring-1 focus:ring-indigo-400" />
          </div>
          <div v-if="filteredMembers.length === 0" class="px-3 py-2 text-xs text-gray-400">Aucun membre</div>
          <button v-for="m in filteredMembers" :key="m.user_id" type="button" @click="insertMember(m)"
            class="w-full text-left flex items-center gap-2 px-3 py-2 hover:bg-gray-50 transition-colors">
            <UserAvatar :src="(resolveMediaUrl(m.profile_picture_file, 64) ?? m.profile_picture_url) ?? undefined" :name="m.full_name || m.email" size="sm" />
            <div>
              <p class="text-sm font-medium text-gray-800">{{ m.full_name || m.email }}</p>
              <p v-if="m.title" class="text-xs text-indigo-600">{{ m.title }}</p>
            </div>
          </button>
        </div>
      </div>

      <!-- Insert image -->
      <div class="relative" ref="imageDropdownRef">
        <button type="button" @click="toggleImagePanel" class="toolbar-btn flex items-center gap-1"
          title="Insérer une image">
          <PhotoIcon class="h-4 w-4" />
          <span class="text-xs">Image</span>
        </button>
        <div v-if="showImagePanel"
          class="absolute left-0 top-full mt-1 z-50 bg-white shadow-lg rounded-lg border border-gray-200 w-72">
          <!-- Upload new image -->
          <div class="p-3 border-b border-gray-100">
            <p class="text-xs font-semibold text-gray-600 mb-2">Téléverser une image</p>
            <label class="flex items-center gap-2 cursor-pointer text-sm text-indigo-600 hover:text-indigo-800">
              <ArrowUpTrayIcon class="h-4 w-4" />
              Choisir un fichier
              <input type="file" accept="image/*" class="hidden" @change="uploadImage" ref="fileInputRef" />
            </label>
            <p v-if="uploadError" class="text-xs text-red-500 mt-1">{{ uploadError }}</p>
            <p v-if="uploading" class="text-xs text-gray-400 mt-1">Envoi en cours...</p>
          </div>

          <!-- Existing images -->
          <div class="p-2 max-h-48 overflow-y-auto">
            <p class="text-xs font-semibold text-gray-500 mb-2 px-1">Images de l'organisation</p>
            <div v-if="images.length === 0" class="text-xs text-gray-400 px-1 pb-2">Aucune image</div>
            <div class="grid grid-cols-3 gap-1">
              <div v-for="img in images" :key="img.id" class="relative group">
                <button type="button" @click="insertImage(img)"
                  class="w-full aspect-square rounded overflow-hidden border border-gray-200 hover:border-indigo-300 transition-colors">
                  <img :src="img.url ?? undefined" :alt="img.filename" class="w-full h-full object-cover" />
                </button>
                <button type="button" @click="deleteImage(img)"
                  class="absolute top-0.5 right-0.5 hidden group-hover:flex h-5 w-5 items-center justify-center rounded-full bg-red-500 text-white"
                  title="Supprimer">
                  <XMarkIcon class="h-3 w-3" />
                </button>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Textarea -->
    <textarea ref="textareaRef" :value="modelValue" @input="$emit('update:modelValue', ($event.target as HTMLTextAreaElement).value)" rows="12"
      placeholder="Écrivez une description... Utilisez la barre d'outils pour insérer des membres ou des images."
      class="block w-full rounded-b-lg border border-gray-200 px-3 py-2 text-gray-900 placeholder:text-gray-400 focus:ring-2 focus:ring-inset focus:ring-indigo-600 sm:text-sm font-mono leading-relaxed resize-y"></textarea>

    <!-- Help -->
    <p class="mt-1 text-xs text-gray-400">
      Syntaxe : <code>**gras**</code>, <code>*italique*</code>, <code># titre</code>, <code>@[Nom Membre]</code>,
      <code>![alt](url)</code>
    </p>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, onBeforeUnmount } from 'vue'
import { UserCircleIcon, PhotoIcon, ArrowUpTrayIcon, XMarkIcon } from '@heroicons/vue/24/outline'
import UserAvatar from './UserAvatar.vue'
import { api } from '@/api'
import { resolveMediaUrl } from '../utils/media'
import type { OrganizationImageRead } from '@/api/types'

interface MemberOption {
  user_id: string
  email: string
  full_name: string | null
  profile_picture_url: string | null
  profile_picture_file: import('@/api/types').StoredFileRead | null
  title?: string | null
}

const props = defineProps({
  modelValue: { type: String, default: '' },
  organizationId: { type: String, required: true },
  members: { type: Array as () => MemberOption[], default: () => [] }
})

const emit = defineEmits(['update:modelValue', 'images-updated'])

const textareaRef = ref<HTMLTextAreaElement | null>(null)
const fileInputRef = ref<HTMLInputElement | null>(null)
const memberDropdownRef = ref<HTMLElement | null>(null)
const imageDropdownRef = ref<HTMLElement | null>(null)

const showMemberDropdown = ref(false)
const showImagePanel = ref(false)
const memberSearch = ref('')
const images = ref<OrganizationImageRead[]>([])
const uploading = ref(false)
const uploadError = ref('')

const filteredMembers = computed(() => {
  const q = memberSearch.value.toLowerCase()
  return props.members.filter(m =>
    (m.full_name || m.email || '').toLowerCase().includes(q) ||
    (m.title || '').toLowerCase().includes(q)
  )
})

const loadImages = async () => {
  try {
    images.value = await api.organization_images.list_organization_images(props.organizationId)
    emit('images-updated', images.value)
  } catch (e) {
    console.error('Failed to load images', e)
  }
}

const toggleImagePanel = async () => {
  showImagePanel.value = !showImagePanel.value
  if (showImagePanel.value) {
    await loadImages()
  }
}

const uploadImage = async (event: Event) => {
  const file = (event.target as HTMLInputElement).files?.[0]
  if (!file) return
  uploading.value = true
  uploadError.value = ''
  try {
    const formData = new FormData()
    formData.append('file', file)
    const res = await api.organization_images.upload_organization_image(props.organizationId, formData)
    images.value.push(res)
    emit('images-updated', images.value)
    // Auto-insert
    insertImage(res)
  } catch (e: any) {
    uploadError.value = e.response?.data?.detail || "Échec de l'upload"
  } finally {
    uploading.value = false
    if (fileInputRef.value) fileInputRef.value.value = ''
  }
}

const deleteImage = async (img: OrganizationImageRead) => {
  if (!confirm(`Supprimer l'image "${img.filename}" ?`)) return
  try {
    await api.organization_images.delete_organization_image(props.organizationId, img.id)
    images.value = images.value.filter(i => i.id !== img.id)
    emit('images-updated', images.value)
  } catch (e) {
    console.error('Failed to delete image', e)
  }
}

// --- Textarea helpers ---

function getSelection() {
  const ta = textareaRef.value
  if (!ta) return { start: 0, end: 0, selected: '' }
  return { start: ta.selectionStart, end: ta.selectionEnd, selected: ta.value.slice(ta.selectionStart, ta.selectionEnd) }
}

function replaceSelection(newText: string, cursorOffset: number | null = null) {
  const ta = textareaRef.value
  if (!ta) return
  const { start, end } = getSelection()
  const before = ta.value.slice(0, start)
  const after = ta.value.slice(end)
  const updated = before + newText + after
  emit('update:modelValue', updated)
  // Restore cursor after Vue re-renders
  setTimeout(() => {
    const pos = cursorOffset !== null ? start + cursorOffset : start + newText.length
    ta.focus()
    ta.setSelectionRange(pos, pos)
  }, 0)
}

function insert(prefix: string, suffix = '') {
  const { selected } = getSelection()
  const inner = selected || 'texte'
  replaceSelection(prefix + inner + suffix, prefix.length + inner.length + suffix.length)
}


function insertListItem() {
  replaceSelection('\n- ')
}

function insertHr() {
  replaceSelection('\n\n---\n\n')
}

function insertMember(member: MemberOption) {
  const line = `\n@[${member.user_id}]\n`
  replaceSelection(line)
  showMemberDropdown.value = false
  memberSearch.value = ''
}

function insertImage(img: OrganizationImageRead) {
  const filename = img.filename.replace("_", " ").replace(".png", "").replace(".jpg", "").replace(".jpeg", "").replace(".gif", "").replace(".webp", "").replace(".svg", "")
  const line = `\n![${filename}](${img.url})\n`
  replaceSelection(line)
  showImagePanel.value = false
}

// Close dropdowns on outside click
function handleOutsideClick(e: MouseEvent) {
  if (memberDropdownRef.value && !memberDropdownRef.value.contains(e.target as Node | null)) {
    showMemberDropdown.value = false
  }
  if (imageDropdownRef.value && !imageDropdownRef.value.contains(e.target as Node | null)) {
    showImagePanel.value = false
  }
}

onMounted(() => {
  document.addEventListener('mousedown', handleOutsideClick)
  loadImages()
})
onBeforeUnmount(() => {
  document.removeEventListener('mousedown', handleOutsideClick)
})
</script>

<style scoped>
.toolbar-btn {
  padding: 0.25rem 0.5rem;
  font-size: 0.75rem;
  line-height: 1rem;
  border-radius: 0.25rem;
  border: 1px solid #e5e7eb;
  background-color: #ffffff;
  color: #374151;
  transition: background-color 0.15s;
}

.toolbar-btn:hover {
  background-color: #f3f4f6;
}
</style>
