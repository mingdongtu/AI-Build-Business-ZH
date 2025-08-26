import { describe, it, expect, vi, beforeEach } from 'vitest'
import { mount } from '@vue/test-utils'
import ScoreDisplay from '@/components/ScoreDisplay.vue'

describe('ScoreDisplay.vue', () => {
  // Mock navigator.share
  let navigatorShareMock
  
  beforeEach(() => {
    // Reset mocks
    vi.clearAllMocks()
    
    // Mock navigator.share
    navigatorShareMock = vi.fn().mockResolvedValue({})
    global.navigator.share = navigatorShareMock
    
    // Mock document.execCommand
    document.execCommand = vi.fn().mockReturnValue(true)
    
    // Mock document methods for clipboard fallback
    document.createElement = vi.fn().mockImplementation((tagName) => {
      if (tagName === 'textarea') {
        return {
          value: '',
          select: vi.fn(),
          style: {}
        }
      }
      return {}
    })
    document.body.appendChild = vi.fn()
    document.body.removeChild = vi.fn()
    
    // Mock window.alert
    global.alert = vi.fn()
  })
  
  it('renders correctly with props', () => {
    const props = {
      score: 75,
      foodName: '测试食品',
      ingredients: ['糖', '面粉', '盐'],
      healthPoints: [
        { type: 'positive', description: '低钠' },
        { type: 'negative', description: '含有添加糖' }
      ],
      recommendation: '这是一个健康建议'
    }
    
    const wrapper = mount(ScoreDisplay, {
      props
    })
    
    // Check if score is displayed correctly
    expect(wrapper.find('.score-value').text()).toBe('75')
    
    // Check if food name is displayed
    expect(wrapper.text()).toContain('测试食品')
    
    // Check if ingredients are displayed
    props.ingredients.forEach(ingredient => {
      expect(wrapper.text()).toContain(ingredient)
    })
    
    // Check if health points are displayed
    props.healthPoints.forEach(point => {
      expect(wrapper.text()).toContain(point.description)
    })
    
    // Check if recommendation is displayed
    expect(wrapper.text()).toContain(props.recommendation)
  })
  
  it('computes correct score class and label based on score', async () => {
    // Test excellent score
    const excellentWrapper = mount(ScoreDisplay, {
      props: {
        score: 85,
        ingredients: [],
        healthPoints: [],
        recommendation: ''
      }
    })
    expect(excellentWrapper.vm.scoreClass).toBe('excellent')
    expect(excellentWrapper.vm.scoreLabel).toBe('优秀')
    expect(excellentWrapper.find('.score-circle').classes()).toContain('excellent')
    
    // Test good score
    const goodWrapper = mount(ScoreDisplay, {
      props: {
        score: 65,
        ingredients: [],
        healthPoints: [],
        recommendation: ''
      }
    })
    expect(goodWrapper.vm.scoreClass).toBe('good')
    expect(goodWrapper.vm.scoreLabel).toBe('良好')
    
    // Test average score
    const averageWrapper = mount(ScoreDisplay, {
      props: {
        score: 45,
        ingredients: [],
        healthPoints: [],
        recommendation: ''
      }
    })
    expect(averageWrapper.vm.scoreClass).toBe('average')
    expect(averageWrapper.vm.scoreLabel).toBe('一般')
    
    // Test poor score
    const poorWrapper = mount(ScoreDisplay, {
      props: {
        score: 30,
        ingredients: [],
        healthPoints: [],
        recommendation: ''
      }
    })
    expect(poorWrapper.vm.scoreClass).toBe('poor')
    expect(poorWrapper.vm.scoreLabel).toBe('较差')
  })
  
  it('applies correct class to ingredients based on health impact', () => {
    const wrapper = mount(ScoreDisplay, {
      props: {
        score: 50,
        foodName: '',
        ingredients: ['全麦面粉', '白砂糖', '盐', '水'],
        healthPoints: [],
        recommendation: ''
      }
    })
    
    // Get all ingredient items
    const ingredientItems = wrapper.findAll('.ingredient-item')
    
    // Check if healthy ingredient has correct class
    const healthyIngredient = ingredientItems.find(item => item.text().includes('全麦'))
    expect(healthyIngredient.classes()).toContain('healthy')
    
    // Check if unhealthy ingredient has correct class
    const unhealthyIngredient = ingredientItems.find(item => item.text().includes('白砂糖'))
    expect(unhealthyIngredient.classes()).toContain('unhealthy')
    
    // Check if neutral ingredient has no special class
    const neutralIngredient = ingredientItems.find(item => item.text().includes('水'))
    expect(neutralIngredient.classes()).not.toContain('healthy')
    expect(neutralIngredient.classes()).not.toContain('unhealthy')
  })
  
  it('emits analyze-new event when button is clicked', async () => {
    const wrapper = mount(ScoreDisplay, {
      props: {
        score: 70,
        foodName: '',
        ingredients: [],
        healthPoints: [],
        recommendation: ''
      }
    })
    
    // Find and click the analyze new button
    await wrapper.find('.action-button.secondary').trigger('click')
    
    // Check if event was emitted
    expect(wrapper.emitted('analyze-new')).toBeTruthy()
    expect(wrapper.emitted('analyze-new').length).toBe(1)
  })
  
  it('uses Web Share API when available', async () => {
    const wrapper = mount(ScoreDisplay, {
      props: {
        score: 70,
        foodName: '测试食品',
        ingredients: [],
        healthPoints: [],
        recommendation: '健康建议'
      }
    })
    
    // Find and click the share button
    await wrapper.find('.action-button.primary').trigger('click')
    
    // Check if navigator.share was called with correct parameters
    expect(navigatorShareMock).toHaveBeenCalledWith({
      title: '食品健康评分结果',
      text: expect.stringContaining('测试食品'),
      url: expect.any(String)
    })
  })
  
  it('falls back to clipboard when Web Share API is not available', async () => {
    // Remove navigator.share to simulate unsupported browser
    delete global.navigator.share
    
    const wrapper = mount(ScoreDisplay, {
      props: {
        score: 70,
        foodName: '测试食品',
        ingredients: [],
        healthPoints: [],
        recommendation: '健康建议'
      }
    })
    
    // Find and click the share button
    await wrapper.find('.action-button.primary').trigger('click')
    
    // Check if clipboard fallback was used
    expect(document.createElement).toHaveBeenCalledWith('textarea')
    expect(document.execCommand).toHaveBeenCalledWith('copy')
    expect(global.alert).toHaveBeenCalled()
  })
  
  it('handles clipboard errors gracefully', async () => {
    // Remove navigator.share to simulate unsupported browser
    delete global.navigator.share
    
    // Mock document.execCommand to fail
    document.execCommand = vi.fn().mockReturnValue(false)
    
    // Mock console.error
    console.error = vi.fn()
    
    const wrapper = mount(ScoreDisplay, {
      props: {
        score: 70,
        foodName: '测试食品',
        ingredients: [],
        healthPoints: [],
        recommendation: '健康建议'
      }
    })
    
    // Find and click the share button
    await wrapper.find('.action-button.primary').trigger('click')
    
    // Check if error was logged and alert was shown
    expect(console.error).toHaveBeenCalled()
    expect(global.alert).toHaveBeenCalledWith('分享功能不可用，请手动截图分享')
  })
})
