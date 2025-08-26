import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest'
import { mount, flushPromises } from '@vue/test-utils'
import ImageAnalyzer from '@/components/ImageAnalyzer.vue'
import CameraCapture from '@/components/CameraCapture.vue'
import axios from 'axios'
import { createRouter, createWebHistory } from 'vue-router'

// Mock axios
vi.mock('axios')

// Mock router
const router = createRouter({
  history: createWebHistory(),
  routes: [
    {
      path: '/',
      name: 'Home',
    },
    {
      path: '/results',
      name: 'Results',
    }
  ]
})

describe('ImageAnalyzer.vue', () => {
  // Mock localStorage
  let localStorageMock = {}
  
  beforeEach(() => {
    // Reset mocks before each test
    vi.clearAllMocks()
    
    // Mock localStorage
    localStorageMock = {}
    Storage.prototype.setItem = vi.fn((key, value) => {
      localStorageMock[key] = value
    })
    Storage.prototype.getItem = vi.fn(key => localStorageMock[key])
    
    // Mock environment variables
    process.env.VUE_APP_API_URL = 'http://test-api.com'
    
    // Mock window.URL.createObjectURL
    global.URL.createObjectURL = vi.fn(() => 'mock-url')
  })
  
  it('renders correctly in initial state', () => {
    const wrapper = mount(ImageAnalyzer, {
      global: {
        components: {
          CameraCapture
        },
        plugins: [router]
      }
    })
    
    // Check initial state
    expect(wrapper.vm.isAnalyzing).toBe(false)
    expect(wrapper.vm.analysisComplete).toBe(false)
    expect(wrapper.vm.analysisError).toBeNull()
    
    // Check if CameraCapture component is rendered
    expect(wrapper.findComponent(CameraCapture).exists()).toBe(true)
  })
  
  it('starts analysis when image is captured', async () => {
    const wrapper = mount(ImageAnalyzer, {
      global: {
        components: {
          CameraCapture
        },
        plugins: [router]
      }
    })
    
    // Mock successful API response
    axios.post.mockResolvedValue({
      data: {
        score: 85,
        ingredients: ['sugar', 'flour'],
        health_points: [
          { type: 'positive', description: 'Low sodium' }
        ],
        recommendation: 'Good choice'
      }
    })
    
    // Create a mock file
    const mockFile = new File([''], 'test.jpg', { type: 'image/jpeg' })
    
    // Trigger image captured event
    wrapper.vm.handleImageCaptured({ file: mockFile })
    
    // Check if analysis started
    expect(wrapper.vm.isAnalyzing).toBe(true)
    expect(wrapper.find('.analyzing-section').exists()).toBe(true)
    
    // Wait for API call to resolve
    await flushPromises()
    
    // Check if API was called with correct parameters
    expect(axios.post).toHaveBeenCalledWith(
      'http://test-api.com/analyze',
      expect.any(FormData),
      expect.objectContaining({
        headers: { 'Content-Type': 'multipart/form-data' }
      })
    )
    
    // Check if results were stored in localStorage
    expect(localStorage.setItem).toHaveBeenCalledWith(
      'analysisResults',
      expect.any(String)
    )
    
    // Check if router was called to navigate to results page
    expect(router.currentRoute.value.path).toBe('/results')
  })
  
  it('handles API error correctly', async () => {
    const wrapper = mount(ImageAnalyzer, {
      global: {
        components: {
          CameraCapture
        },
        plugins: [router]
      }
    })
    
    // Mock API error
    axios.post.mockRejectedValue({
      response: {
        status: 422
      }
    })
    
    // Create a mock file
    const mockFile = new File([''], 'test.jpg', { type: 'image/jpeg' })
    
    // Trigger image captured event
    wrapper.vm.handleImageCaptured({ file: mockFile })
    
    // Wait for API call to reject
    await flushPromises()
    
    // Check if error state is set correctly
    expect(wrapper.vm.isAnalyzing).toBe(false)
    expect(wrapper.vm.analysisError).toBe('无法识别图片中的配料表，请确保图片清晰且包含配料表')
    expect(wrapper.find('.error-section').exists()).toBe(true)
  })
  
  it('handles different types of API errors', async () => {
    const wrapper = mount(ImageAnalyzer, {
      global: {
        components: {
          CameraCapture
        },
        plugins: [router]
      }
    })
    
    // Test case 1: File too large (413)
    axios.post.mockRejectedValueOnce({
      response: {
        status: 413
      }
    })
    
    wrapper.vm.handleImageCaptured({ file: new File([''], 'large.jpg') })
    await flushPromises()
    expect(wrapper.vm.analysisError).toBe('图片文件太大，请使用较小的图片')
    
    // Test case 2: Network error
    axios.post.mockRejectedValueOnce({
      request: {}
    })
    
    wrapper.vm.handleImageCaptured({ file: new File([''], 'test.jpg') })
    await flushPromises()
    expect(wrapper.vm.analysisError).toBe('服务器无响应，请检查网络连接后重试')
    
    // Test case 3: Timeout
    axios.post.mockRejectedValueOnce({
      code: 'ECONNABORTED'
    })
    
    wrapper.vm.handleImageCaptured({ file: new File([''], 'test.jpg') })
    await flushPromises()
    expect(wrapper.vm.analysisError).toBe('请求超时，服务器处理时间过长，请稍后重试')
  })
  
  it('resets analysis state correctly', async () => {
    const wrapper = mount(ImageAnalyzer, {
      global: {
        components: {
          CameraCapture
        },
        plugins: [router]
      }
    })
    
    // Set error state
    wrapper.vm.isAnalyzing = false
    wrapper.vm.analysisComplete = false
    wrapper.vm.analysisError = '测试错误'
    wrapper.vm.capturedImage = { file: new File([''], 'test.jpg') }
    
    // Call reset method
    wrapper.vm.resetAnalysis()
    
    // Check if state was reset
    expect(wrapper.vm.isAnalyzing).toBe(false)
    expect(wrapper.vm.analysisComplete).toBe(false)
    expect(wrapper.vm.analysisError).toBeNull()
    expect(wrapper.vm.capturedImage).toBeNull()
  })
  
  it('loading animation works correctly', async () => {
    vi.useFakeTimers()
    
    const wrapper = mount(ImageAnalyzer, {
      global: {
        components: {
          CameraCapture
        },
        plugins: [router]
      }
    })
    
    // Start loading animation
    wrapper.vm.startLoadingAnimation()
    
    // Check initial step
    expect(wrapper.vm.currentStepIndex).toBe(0)
    expect(wrapper.vm.loadingStep).toBe('识别图片中...')
    
    // Advance timer by 2 seconds
    vi.advanceTimersByTime(2000)
    
    // Check if step was updated
    expect(wrapper.vm.currentStepIndex).toBe(1)
    expect(wrapper.vm.loadingStep).toBe('提取配料信息...')
    
    // Stop loading animation
    wrapper.vm.stopLoadingAnimation()
    
    // Advance timer again
    vi.advanceTimersByTime(2000)
    
    // Check if animation was stopped
    expect(wrapper.vm.currentStepIndex).toBe(1)
    
    vi.useRealTimers()
  })
  
  it('cleans up interval on component unmount', async () => {
    const wrapper = mount(ImageAnalyzer, {
      global: {
        components: {
          CameraCapture
        },
        plugins: [router]
      }
    })
    
    // Spy on clearInterval
    const clearIntervalSpy = vi.spyOn(window, 'clearInterval')
    
    // Start loading animation
    wrapper.vm.startLoadingAnimation()
    
    // Unmount component
    wrapper.unmount()
    
    // Check if interval was cleared
    expect(clearIntervalSpy).toHaveBeenCalled()
  })
})
