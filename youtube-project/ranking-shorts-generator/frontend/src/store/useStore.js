import { create } from 'zustand'
import { devtools } from 'zustand/middleware'

const useStore = create(
  devtools((set, get) => ({
    // Search state
    searches: [],
    currentSearch: null,
    searchLoading: false,

    // Videos state
    videos: [],
    selectedVideos: [],
    videosLoading: false,

    // Project state
    projects: [],
    currentProject: null,
    projectLoading: false,

    // Generation state
    generationProgress: 0,
    generationStatus: 'idle', // idle, processing, completed, failed
    generationMessage: '',

    // UI state
    sidebarOpen: true,
    modalOpen: false,
    modalContent: null,

    // Actions - Search
    setSearches: (searches) => set({ searches }),
    setCurrentSearch: (search) => set({ currentSearch: search }),
    setSearchLoading: (loading) => set({ searchLoading: loading }),

    addSearch: (search) =>
      set((state) => ({
        searches: [search, ...state.searches],
      })),

    // Actions - Videos
    setVideos: (videos) => set({ videos }),
    setVideosLoading: (loading) => set({ videosLoading: loading }),

    setSelectedVideos: (videos) => set({ selectedVideos: videos }),

    toggleVideoSelection: (video) =>
      set((state) => {
        const isSelected = state.selectedVideos.find((v) => v.id === video.id)
        if (isSelected) {
          return {
            selectedVideos: state.selectedVideos.filter((v) => v.id !== video.id),
          }
        } else {
          // 최대 10개까지만 선택 가능
          if (state.selectedVideos.length >= 10) {
            return state
          }
          return {
            selectedVideos: [...state.selectedVideos, video],
          }
        }
      }),

    reorderSelectedVideos: (startIndex, endIndex) =>
      set((state) => {
        const result = Array.from(state.selectedVideos)
        const [removed] = result.splice(startIndex, 1)
        result.splice(endIndex, 0, removed)
        return { selectedVideos: result }
      }),

    clearSelectedVideos: () => set({ selectedVideos: [] }),

    // Actions - Projects
    setProjects: (projects) => set({ projects }),
    setCurrentProject: (project) => set({ currentProject: project }),
    setProjectLoading: (loading) => set({ projectLoading: loading }),

    addProject: (project) =>
      set((state) => ({
        projects: [project, ...state.projects],
      })),

    // Actions - Generation
    setGenerationProgress: (progress) => set({ generationProgress: progress }),
    setGenerationStatus: (status) => set({ generationStatus: status }),
    setGenerationMessage: (message) => set({ generationMessage: message }),

    updateGenerationState: (state) =>
      set({
        generationProgress: state.progress || get().generationProgress,
        generationStatus: state.status || get().generationStatus,
        generationMessage: state.message || get().generationMessage,
      }),

    resetGeneration: () =>
      set({
        generationProgress: 0,
        generationStatus: 'idle',
        generationMessage: '',
      }),

    // Actions - UI
    toggleSidebar: () => set((state) => ({ sidebarOpen: !state.sidebarOpen })),
    setSidebarOpen: (open) => set({ sidebarOpen: open }),

    openModal: (content) => set({ modalOpen: true, modalContent: content }),
    closeModal: () => set({ modalOpen: false, modalContent: null }),
  }))
)

export default useStore
