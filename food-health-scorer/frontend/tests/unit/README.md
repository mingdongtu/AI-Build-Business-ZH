# Unit Testing Guide for Food Health Scorer

This guide outlines the unit testing approach for the Food Health Scorer application using Vue Test Utils and Jest.

## Testing Setup

### Required Dependencies

```bash
npm install --save-dev @vue/test-utils@next jest vue-jest@next babel-jest @babel/preset-env jest-transform-stub
```

### Jest Configuration

Add to `package.json`:

```json
"jest": {
  "moduleFileExtensions": [
    "js",
    "vue"
  ],
  "transform": {
    "^.+\\.vue$": "vue-jest",
    "^.+\\.js$": "babel-jest",
    "^.+\\.(png|jpg|jpeg|gif|svg|webp)$": "jest-transform-stub"
  },
  "moduleNameMapper": {
    "^@/(.*)$": "<rootDir>/src/$1"
  },
  "testEnvironment": "jsdom"
}
```

## Component Testing Strategy

### 1. CameraCapture.vue

Test cases:
- Verify camera initialization
- Test fallback to file upload when camera is not available
- Validate image capture functionality
- Ensure proper error handling

```javascript
// Example test for CameraCapture.vue
import { mount } from '@vue/test-utils'
import CameraCapture from '@/components/CameraCapture.vue'

describe('CameraCapture.vue', () => {
  // Mock navigator.mediaDevices
  const mockMediaDevices = {
    getUserMedia: jest.fn().mockResolvedValue('mock-stream')
  }
  
  beforeEach(() => {
    global.navigator.mediaDevices = mockMediaDevices
  })
  
  test('initializes camera when component is mounted', async () => {
    const wrapper = mount(CameraCapture)
    await wrapper.vm.$nextTick()
    
    expect(mockMediaDevices.getUserMedia).toHaveBeenCalled()
    expect(wrapper.vm.cameraActive).toBe(true)
  })
  
  test('shows file upload fallback when camera is not available', async () => {
    mockMediaDevices.getUserMedia.mockRejectedValueOnce(new Error('Camera not available'))
    
    const wrapper = mount(CameraCapture)
    await wrapper.vm.$nextTick()
    
    expect(wrapper.vm.cameraError).toBe(true)
    expect(wrapper.find('.fallback-upload').exists()).toBe(true)
  })
})
```

### 2. ImageAnalyzer.vue

Test cases:
- Test loading state transitions
- Verify API call with correct parameters
- Test error handling for different error scenarios
- Validate navigation after successful analysis

```javascript
// Example test for ImageAnalyzer.vue
import { mount, flushPromises } from '@vue/test-utils'
import ImageAnalyzer from '@/components/ImageAnalyzer.vue'
import axios from 'axios'

jest.mock('axios')

describe('ImageAnalyzer.vue', () => {
  test('shows loading state when analyzing image', async () => {
    axios.post.mockResolvedValue({ data: { score: 85 } })
    
    const wrapper = mount(ImageAnalyzer)
    wrapper.vm.handleImageCaptured({ file: new File([''], 'test.jpg') })
    
    expect(wrapper.vm.isAnalyzing).toBe(true)
    expect(wrapper.find('.analyzing-section').exists()).toBe(true)
  })
  
  test('handles API error correctly', async () => {
    axios.post.mockRejectedValue({ response: { status: 422 } })
    
    const wrapper = mount(ImageAnalyzer)
    wrapper.vm.handleImageCaptured({ file: new File([''], 'test.jpg') })
    
    await flushPromises()
    
    expect(wrapper.vm.isAnalyzing).toBe(false)
    expect(wrapper.vm.analysisError).toBeTruthy()
    expect(wrapper.find('.error-section').exists()).toBe(true)
  })
})
```

### 3. ScoreDisplay.vue

Test cases:
- Verify correct score class based on score value
- Test rendering of ingredients and health points
- Validate share functionality
- Test event emission when "analyze new" is clicked

```javascript
// Example test for ScoreDisplay.vue
import { mount } from '@vue/test-utils'
import ScoreDisplay from '@/components/ScoreDisplay.vue'

describe('ScoreDisplay.vue', () => {
  test('applies correct score class based on score value', () => {
    const wrapperExcellent = mount(ScoreDisplay, {
      props: {
        score: 85,
        ingredients: [],
        healthPoints: [],
        recommendation: ''
      }
    })
    
    const wrapperPoor = mount(ScoreDisplay, {
      props: {
        score: 30,
        ingredients: [],
        healthPoints: [],
        recommendation: ''
      }
    })
    
    expect(wrapperExcellent.vm.scoreClass).toBe('excellent')
    expect(wrapperPoor.vm.scoreClass).toBe('poor')
  })
  
  test('emits analyze-new event when button is clicked', async () => {
    const wrapper = mount(ScoreDisplay, {
      props: {
        score: 70,
        ingredients: [],
        healthPoints: [],
        recommendation: ''
      }
    })
    
    await wrapper.find('.action-button.secondary').trigger('click')
    
    expect(wrapper.emitted('analyze-new')).toBeTruthy()
  })
})
```

### 4. HomeView.vue and ResultsView.vue

Test cases:
- Verify component rendering
- Test child component integration
- Validate navigation functionality

```javascript
// Example test for HomeView.vue
import { mount } from '@vue/test-utils'
import HomeView from '@/views/HomeView.vue'
import ImageAnalyzer from '@/components/ImageAnalyzer.vue'

describe('HomeView.vue', () => {
  test('renders ImageAnalyzer component', () => {
    const wrapper = mount(HomeView)
    
    expect(wrapper.findComponent(ImageAnalyzer).exists()).toBe(true)
  })
})

// Example test for ResultsView.vue
import { mount, flushPromises } from '@vue/test-utils'
import ResultsView from '@/views/ResultsView.vue'
import ScoreDisplay from '@/components/ScoreDisplay.vue'

describe('ResultsView.vue', () => {
  beforeEach(() => {
    // Mock localStorage
    Storage.prototype.getItem = jest.fn()
  })
  
  test('shows no-results when no analysis data is available', () => {
    Storage.prototype.getItem.mockReturnValue(null)
    
    const wrapper = mount(ResultsView)
    
    expect(wrapper.find('.no-results').exists()).toBe(true)
    expect(wrapper.findComponent(ScoreDisplay).exists()).toBe(false)
  })
  
  test('renders ScoreDisplay when results are available', () => {
    const mockResults = {
      score: 75,
      ingredients: ['sugar', 'flour'],
      health_points: [{ type: 'positive', description: 'Low sodium' }],
      recommendation: 'Good choice'
    }
    
    Storage.prototype.getItem.mockReturnValue(JSON.stringify(mockResults))
    
    const wrapper = mount(ResultsView)
    
    expect(wrapper.findComponent(ScoreDisplay).exists()).toBe(true)
    expect(wrapper.findComponent(ScoreDisplay).props('score')).toBe(75)
  })
})
```

## API Testing

For testing API calls, use Jest's mocking capabilities:

```javascript
// Example API test
import axios from 'axios'
import { analyzeImage } from '@/services/api'

jest.mock('axios')

describe('API Service', () => {
  test('analyzeImage sends correct request', async () => {
    const mockFile = new File([''], 'test.jpg')
    const mockResponse = { data: { score: 80 } }
    
    axios.post.mockResolvedValue(mockResponse)
    
    const result = await analyzeImage(mockFile)
    
    expect(axios.post).toHaveBeenCalledWith(
      expect.stringContaining('/analyze'),
      expect.any(FormData),
      expect.objectContaining({
        headers: { 'Content-Type': 'multipart/form-data' }
      })
    )
    
    expect(result).toEqual(mockResponse.data)
  })
})
```

## Running Tests

Add to `package.json` scripts:

```json
"scripts": {
  "test:unit": "jest",
  "test:watch": "jest --watch"
}
```

Run tests with:

```bash
npm run test:unit
```

## Best Practices

1. **Test in isolation**: Mock dependencies to isolate the component being tested
2. **Test behavior, not implementation**: Focus on what the component does, not how it does it
3. **Use data-test attributes**: Add `data-test="my-element"` to elements you want to select in tests
4. **Keep tests simple**: Each test should verify one specific behavior
5. **Test edge cases**: Include tests for error states, empty states, and boundary conditions
