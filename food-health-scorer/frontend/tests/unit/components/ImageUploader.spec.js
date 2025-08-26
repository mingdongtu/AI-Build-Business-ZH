import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest'
import { mount } from '@vue/test-utils'
import ImageUploader from '@/components/ImageUploader.vue'
import axios from 'axios'

// Mock axios
vi.mock('axios')

describe('ImageUploader.vue', () => {
  let wrapper
  
  // Mock URL methods
  global.URL.createObjectURL = vi.fn(() => 'mock-url')
  global.URL.revokeObjectURL = vi.fn()
  
  // Mock canvas and blob
  const mockCanvas = {
    getContext: vi.fn(() => ({
      drawImage: vi.fn()
    })),
    toBlob: vi.fn(callback => callback(new Blob([''], { type: 'image/jpeg' })))
  }
  
  global.document.createElement = vi.fn(tag => {
    if (tag === 'canvas') return mockCanvas
    return document.createElement(tag)
  })
  
  // Mock media devices
  const mockMediaDevices = {
    getUserMedia: vi.fn().mockResolvedValue('mock-stream')
  }
  
  beforeEach(() => {
    // Reset mocks
    vi.clearAllMocks()
    
    // Setup navigator mock
    Object.defineProperty(global.navigator, 'mediaDevices', {
      value: mockMediaDevices,
      writable: true
    })
    
    // Mount component
    wrapper = mount(ImageUploader)
  })
  
  afterEach(() => {
    wrapper.unmount()
  })
  
  it('renders correctly', () => {
    expect(wrapper.find('.image-uploader').exists()).toBe(true)
    expect(wrapper.find('.select-container').exists()).toBe(true)
    expect(wrapper.find('.camera-btn').exists()).toBe(true)
  })
  
  it('allows file selection', async () => {
    const file = new File([''], 'test.jpg', { type: 'image/jpeg' })
    const input = wrapper.find('input[type="file"]')
    
    // Trigger file selection
    await input.trigger('change', {
      target: {
        files: [file]
      }
    })
    
    // Check if preview is shown
    expect(wrapper.vm.imageFile).toBe(file)
    expect(wrapper.vm.imagePreview).toBe('mock-url')
    expect(URL.createObjectURL).toHaveBeenCalledWith(file)
    expect(wrapper.find('.image-preview').exists()).toBe(true)
  })
  
  it('validates file type', async () => {
    const file = new File([''], 'test.txt', { type: 'text/plain' })
    const input = wrapper.find('input[type="file"]')
    
    // Trigger file selection with invalid type
    await input.trigger('change', {
      target: {
        files: [file]
      }
    })
    
    // Check error message
    expect(wrapper.vm.errorMessage).toBe('请选择图片文件')
    expect(wrapper.find('.error-message').text()).toBe('请选择图片文件')
  })
  
  it('initializes camera when camera button is clicked', async () => {
    const cameraBtn = wrapper.find('.camera-btn')
    await cameraBtn.trigger('click')
    
    expect(wrapper.vm.showCamera).toBe(true)
    expect(navigator.mediaDevices.getUserMedia).toHaveBeenCalled()
    expect(wrapper.find('.camera-container').exists()).toBe(true)
  })
  
  it('handles camera errors', async () => {
    // Mock camera error
    mockMediaDevices.getUserMedia.mockRejectedValueOnce(new Error('Camera access denied'))
    
    const cameraBtn = wrapper.find('.camera-btn')
    await cameraBtn.trigger('click')
    
    // Wait for async operation to complete
    await wrapper.vm.$nextTick()
    
    expect(wrapper.vm.showCamera).toBe(false)
    expect(wrapper.vm.errorMessage).toContain('无法访问相机')
    expect(wrapper.find('.error-message').exists()).toBe(true)
  })
  
  it('captures image from camera', async () => {
    // Setup video element mock
    const mockVideoElement = {
      srcObject: null,
      videoWidth: 640,
      videoHeight: 480
    }
    
    // Mount with refs
    wrapper = mount(ImageUploader, {
      attachTo: document.body
    })
    
    // Set video element ref
    wrapper.vm.$refs.videoElement = mockVideoElement
    
    // Enable camera
    await wrapper.vm.toggleCamera(true)
    
    // Capture image
    await wrapper.vm.captureImage()
    
    // Check if image was captured
    expect(mockCanvas.getContext).toHaveBeenCalledWith('2d')
    expect(mockCanvas.toBlob).toHaveBeenCalled()
    expect(wrapper.vm.imagePreview).toBe('mock-url')
    expect(wrapper.vm.showCamera).toBe(false)
  })
  
  it('uploads image successfully', async () => {
    // Setup mock response
    const mockResponse = {
      data: {
        score: 85,
        health_points: ['Low sugar', 'High fiber'],
        recommendations: ['Good choice']
      }
    }
    axios.post.mockResolvedValueOnce(mockResponse)
    
    // Set image file
    wrapper.vm.imageFile = new File([''], 'test.jpg', { type: 'image/jpeg' })
    wrapper.vm.imagePreview = 'mock-url'
    
    // Upload image
    await wrapper.vm.uploadImage()
    
    // Check if upload was successful
    expect(axios.post).toHaveBeenCalled()
    expect(wrapper.vm.isUploading).toBe(false)
    expect(wrapper.emitted('analysis-complete')).toBeTruthy()
    expect(wrapper.emitted('analysis-complete')[0][0]).toEqual(mockResponse.data)
  })
  
  it('handles upload errors', async () => {
    // Setup mock error
    const errorResponse = {
      response: {
        data: {
          detail: 'Invalid image format'
        },
        statusText: 'Bad Request'
      }
    }
    axios.post.mockRejectedValueOnce(errorResponse)
    
    // Set image file
    wrapper.vm.imageFile = new File([''], 'test.jpg', { type: 'image/jpeg' })
    wrapper.vm.imagePreview = 'mock-url'
    
    // Upload image
    await wrapper.vm.uploadImage()
    
    // Check if error was handled
    expect(axios.post).toHaveBeenCalled()
    expect(wrapper.vm.isUploading).toBe(false)
    expect(wrapper.vm.errorMessage).toContain('服务器错误')
    expect(wrapper.find('.error-message').exists()).toBe(true)
  })
  
  it('handles network errors', async () => {
    // Setup mock network error
    const networkError = {
      request: {},
      message: 'Network Error'
    }
    axios.post.mockRejectedValueOnce(networkError)
    
    // Set image file
    wrapper.vm.imageFile = new File([''], 'test.jpg', { type: 'image/jpeg' })
    wrapper.vm.imagePreview = 'mock-url'
    
    // Upload image
    await wrapper.vm.uploadImage()
    
    // Check if error was handled
    expect(wrapper.vm.errorMessage).toBe('网络错误: 无法连接到服务器')
  })
  
  it('resets image correctly', async () => {
    // Set image file and preview
    wrapper.vm.imageFile = new File([''], 'test.jpg', { type: 'image/jpeg' })
    wrapper.vm.imagePreview = 'mock-url'
    
    // Reset image
    await wrapper.vm.resetImage()
    
    // Check if reset was successful
    expect(wrapper.vm.imageFile).toBeNull()
    expect(wrapper.vm.imagePreview).toBeNull()
    expect(URL.revokeObjectURL).toHaveBeenCalledWith('mock-url')
  })
  
  it('cleans up resources when unmounted', () => {
    // Mock stream
    const mockTrack = { stop: vi.fn() }
    wrapper.vm.stream = { getTracks: vi.fn(() => [mockTrack]) }
    wrapper.vm.imagePreview = 'mock-url'
    
    // Unmount component
    wrapper.unmount()
    
    // Check if resources were cleaned up
    expect(mockTrack.stop).toHaveBeenCalled()
    expect(URL.revokeObjectURL).toHaveBeenCalledWith('mock-url')
  })
})
