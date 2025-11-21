# Frontend 前端模块

[根目录](../../CLAUDE.md) > [src](../) > **frontend**

## 变更记录 (Changelog)
- **2025-01-21**: 初始化模块文档，分析React前端架构和组件结构

## 模块职责
Frontend 前端模块提供 Parallax 分布式AI推理引擎的Web用户界面，负责：
- 现代化的React用户界面
- 实时聊天对话交互
- 分布式集群管理和监控
- 节点配置和加入向导
- 响应式设计和主题系统

## 技术栈

### 核心框架
- **React**: 19.1.1 - 用户界面库
- **TypeScript**: 5.8.3 - 类型安全的JavaScript
- **Vite**: 7.1.2 - 快速构建工具
- **React Router**: 7.9.1 - 客户端路由

### UI组件库
- **Material-UI**: 7.3.2 - React组件库
- **Emotion**: 11.14.1 - CSS-in-JS样式库
- **Tabler Icons**: 3.35.0 - 图标库
- **Framer Motion**: 12.23.13 - 动画库

### 开发工具
- **TypeScript ESLint**: 8.39.1 - 代码检查
- **Prettier**: 3.6.2 - 代码格式化
- **ESLint**: 9.33.0 - JavaScript代码检查

## 入口与启动

### 主要入口点
- **应用入口**: `src/main.tsx` - React应用启动点
- **根组件**: `src/App.tsx` - 应用根组件
- **构建脚本**: `package.json` - 项目配置和脚本

### 启动命令
```bash
# 安装依赖
pnpm install

# 开发模式启动
pnpm dev          # 启动开发服务器 (localhost:5173)

# 构建生产版本
pnpm build        # 构建到 dist/ 目录

# 预览生产版本
pnpm preview      # 预览构建结果

# 代码检查和格式化
pnpm lint         # ESLint检查
```

## 应用架构

### 目录结构
```
src/
├── App.tsx                    # 应用根组件
├── main.tsx                   # 应用入口
├── apis/                      # API接口层
│   ├── index.ts              # API导出
│   ├── http.ts               # HTTP客户端
│   ├── data.ts               # 数据类型定义
├── components/                # 可复用组件
│   ├── brand/                # 品牌组件
│   ├── common/               # 通用组件
│   ├── inputs/               # 输入组件
│   └── mui/                  # MUI组件封装
├── pages/                     # 页面组件
│   ├── chat.tsx              # 聊天页面
│   ├── join.tsx              # 节点加入页面
│   └── setup.tsx             # 设置页面
├── router/                    # 路由配置
│   ├── index.tsx             # 路由导出
│   ├── main.tsx              # 主路由
│   └── chat.tsx              # 聊天路由
├── services/                  # 业务服务
│   ├── chat.tsx              # 聊天服务
│   ├── cluster.tsx           # 集群管理服务
│   ├── host.tsx              # 主机管理服务
│   └── index.ts              # 服务导出
└── themes/                    # 主题系统
    ├── index.tsx             # 主题配置
    ├── palette.ts            # 调色板
    ├── typography.ts         # 字体系统
    └── components/           # 组件主题
```

### 路由架构
```typescript
// 路由配置 (src/router/index.tsx)
export const AppRouter: React.FC = () => {
  return (
    <HashRouter>
      <Routes>
        <Route path="/" element={<MainRouter />}>
          <Route index element={<Navigate to="/chat" replace />} />
          <Route path="chat" element={<ChatPage />} />
          <Route path="join" element={<JoinPage />} />
          <Route path="setup" element={<SetupPage />} />
        </Route>
        <Route path="/chat" element={<ChatRouter />}>
          <Route index element={<ChatComponent />} />
        </Route>
      </Routes>
    </HashRouter>
  );
};
```

## 核心组件

### 1. 应用根组件 (App.tsx)

#### 功能特性
- **主题提供者**: 全局主题配置
- **服务提供者**: 业务服务注入
- **路由配置**: 页面路由设置
- **全局样式**: CSS重置和基础样式

#### 组件结构
```typescript
const App: React.FC = () => {
  const hostProps = { /* 主机配置 */ };

  return (
    <StrictMode>
      <HashRouter>
        <ThemeProvider theme={createTheme()}>
          <CssBaseline />
          <Providers hostProps={hostProps}>
            <AppRoot>
              <MainRouter />
              <ChatRouter />
            </AppRoot>
          </Providers>
        </ThemeProvider>
      </HashRouter>
    </StrictMode>
  );
};
```

### 2. 服务提供者 (services/)

#### 聊天服务 (chat.tsx)
```typescript
export const ChatProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const [messages, setMessages] = useState<Message[]>([]);
  const [isConnected, setIsConnected] = useState(false);

  const sendMessage = async (content: string) => {
    // 发送消息到后端
    const response = await chatApi.sendMessage({
      model: "Qwen/Qwen3-0.6B",
      messages: [{ role: "user", content }],
      stream: true
    });

    // 处理流式响应
    for await (const chunk of response) {
      setMessages(prev => [...prev, chunk]);
    }
  };

  return (
    <ChatContext.Provider value={{ messages, sendMessage, isConnected }}>
      {children}
    </ChatContext.Provider>
  );
};
```

#### 集群管理服务 (cluster.tsx)
```typescript
export const ClusterProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const [nodes, setNodes] = useState<Node[]>([]);
  const [metrics, setMetrics] = useState<ClusterMetrics>({});

  const refreshCluster = async () => {
    const clusterInfo = await clusterApi.getClusterInfo();
    setNodes(clusterInfo.nodes);
    setMetrics(clusterInfo.metrics);
  };

  return (
    <ClusterContext.Provider value={{ nodes, metrics, refreshCluster }}>
      {children}
    </ClusterContext.Provider>
  );
};
```

#### 主机管理服务 (host.tsx)
```typescript
export interface HostProps {
  apiUrl: string;
  modelPath: string;
  maxTokens: number;
  temperature: number;
}

export const HostProvider: React.FC<PropsWithChildren<{ hostProps: HostProps }>> = ({
  children,
  hostProps
}) => {
  const [config, setConfig] = useState(hostProps);

  return (
    <HostContext.Provider value={{ config, setConfig }}>
      {children}
    </HostContext.Provider>
  );
};
```

### 3. 页面组件

#### 聊天页面 (pages/chat.tsx)
```typescript
export const ChatPage: React.FC = () => {
  return (
    <DrawerLayout>
      <MainLayout>
        <ChatMessages />
        <ChatInput />
        <NodeList />
        <ModelSelect />
      </MainLayout>
    </DrawerLayout>
  );
};
```

#### 节点加入页面 (pages/join.tsx)
```typescript
export const JoinPage: React.FC = () => {
  return (
    <Container maxWidth="md">
      <Paper elevation={3} sx={{ p: 4, mt: 4 }}>
        <Typography variant="h4" gutterBottom>
          加入 Parallax 集群
        </Typography>
        <JoinCommand />
        <NodeConfiguration />
      </Paper>
    </Container>
  );
};
```

#### 设置页面 (pages/setup.tsx)
```typescript
export const SetupPage: React.FC = () => {
  return (
    <Container maxWidth="lg">
      <Grid container spacing={3}>
        <Grid item xs={12} md={6}>
          <ModelConfiguration />
        </Grid>
        <Grid item xs={12} md={6}>
          <NetworkConfiguration />
        </Grid>
        <Grid item xs={12}>
          <AdvancedSettings />
        </Grid>
      </Grid>
    </Container>
  );
};
```

### 4. 输入组件 (components/inputs/)

#### 聊天输入框 (chat-input.tsx)
```typescript
export const ChatInput: React.FC = () => {
  const [input, setInput] = useState('');
  const { sendMessage } = useChat();

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (input.trim()) {
      await sendMessage(input);
      setInput('');
    }
  };

  return (
    <Box component="form" onSubmit={handleSubmit}>
      <TextField
        fullWidth
        multiline
        maxRows={4}
        value={input}
        onChange={(e) => setInput(e.target.value)}
        placeholder="输入消息..."
        InputProps={{
          endAdornment: (
            <IconButton type="submit" disabled={!input.trim()}>
              <SendIcon />
            </IconButton>
          )
        }}
      />
    </Box>
  );
};
```

#### 节点列表 (node-list.tsx)
```typescript
export const NodeList: React.FC = () => {
  const { nodes } = useCluster();

  return (
    <Paper elevation={1} sx={{ p: 2 }}>
      <Typography variant="h6" gutterBottom>
        集群节点
      </Typography>
      <List>
        {nodes.map((node) => (
          <ListItem key={node.id}>
            <ListItemText
              primary={node.name}
              secondary={`负载: ${node.load}% | 状态: ${node.status}`}
            />
            <Chip
              label={node.status}
              color={node.status === 'active' ? 'success' : 'default'}
            />
          </ListItem>
        ))}
      </List>
    </Paper>
  );
};
```

## API接口层

### HTTP客户端 (apis/http.ts)
```typescript
import axios, { AxiosInstance } from 'axios';

export class HttpClient {
  private client: AxiosInstance;

  constructor(baseURL: string) {
    this.client = axios.create({
      baseURL,
      timeout: 30000,
      headers: {
        'Content-Type': 'application/json',
      },
    });

    this.setupInterceptors();
  }

  private setupInterceptors() {
    // 请求拦截器
    this.client.interceptors.request.use(
      (config) => {
        console.log(`Request: ${config.method?.toUpperCase()} ${config.url}`);
        return config;
      },
      (error) => Promise.reject(error)
    );

    // 响应拦截器
    this.client.interceptors.response.use(
      (response) => response,
      (error) => {
        console.error('API Error:', error.response?.data || error.message);
        return Promise.reject(error);
      }
    );
  }

  async get<T>(url: string, params?: any): Promise<T> {
    const response = await this.client.get(url, { params });
    return response.data;
  }

  async post<T>(url: string, data?: any): Promise<T> {
    const response = await this.client.post(url, data);
    return response.data;
  }

  async stream(url: string, data: any): Promise<AsyncIterable<any>> {
    const response = await fetch(`${this.client.defaults.baseURL}${url}`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(data),
    });

    if (!response.body) {
      throw new Error('Response body is not readable');
    }

    const reader = response.body.getReader();
    const decoder = new TextDecoder();

    return {
      async *[Symbol.asyncIterator]() {
        while (true) {
          const { done, value } = await reader.read();
          if (done) break;

          const chunk = decoder.decode(value);
          const lines = chunk.split('\n');

          for (const line of lines) {
            if (line.startsWith('data: ')) {
              const data = line.slice(6);
              if (data === '[DONE]') return;

              try {
                yield JSON.parse(data);
              } catch (e) {
                // 忽略解析错误
              }
            }
          }
        }
      }
    };
  }
}
```

### 聊天API (apis/data.ts)
```typescript
export interface ChatMessage {
  role: 'user' | 'assistant' | 'system';
  content: string;
}

export interface ChatCompletionRequest {
  model: string;
  messages: ChatMessage[];
  max_tokens?: number;
  temperature?: number;
  stream?: boolean;
}

export interface ChatCompletionResponse {
  id: string;
  object: 'chat.completion';
  created: number;
  model: string;
  choices: Array<{
    index: number;
    message: ChatMessage;
    finish_reason: string;
  }>;
  usage: {
    prompt_tokens: number;
    completion_tokens: number;
    total_tokens: number;
  };
}

export class ChatAPI {
  constructor(private httpClient: HttpClient) {}

  async sendMessage(request: ChatCompletionRequest): Promise<ChatCompletionResponse> {
    return this.httpClient.post<ChatCompletionResponse>('/v1/chat/completions', request);
  }

  async streamMessage(request: ChatCompletionRequest): Promise<AsyncIterable<any>> {
    return this.httpClient.stream('/v1/chat/completions', { ...request, stream: true });
  }

  async getModels(): Promise<any[]> {
    return this.httpClient.get('/v1/models');
  }
}
```

## 主题系统

### 主题配置 (themes/index.tsx)
```typescript
import { createTheme, Theme } from '@mui/material/styles';
import { palette } from './palette';
import { typography } from './typography';
import { components } from './components';

export const createAppTheme = (mode: 'light' | 'dark' = 'light'): Theme => {
  return createTheme({
    palette: palette(mode),
    typography,
    components,
    shape: {
      borderRadius: 12,
    },
    shadows: [
      'none',
      '0px 2px 1px -1px rgba(0,0,0,0.1),0px 1px 1px 0px rgba(0,0,0,0.07),0px 1px 3px 0px rgba(0,0,0,0.06)',
      // ... 更多阴影
    ],
  });
};
```

### 调色板 (themes/palette.ts)
```typescript
export const palette = (mode: 'light' | 'dark') => ({
  mode,
  primary: {
    main: mode === 'light' ? '#1976d2' : '#90caf9',
    light: mode === 'light' ? '#42a5f5' : '#e3f2fd',
    dark: mode === 'light' ? '#1565c0' : '#42a5f5',
  },
  secondary: {
    main: mode === 'light' ? '#dc004e' : '#f48fb1',
  },
  background: {
    default: mode === 'light' ? '#fafafa' : '#121212',
    paper: mode === 'light' ? '#ffffff' : '#1e1e1e',
  },
  text: {
    primary: mode === 'light' ? 'rgba(0, 0, 0, 0.87)' : 'rgba(255, 255, 255, 0.87)',
    secondary: mode === 'light' ? 'rgba(0, 0, 0, 0.6)' : 'rgba(255, 255, 255, 0.6)',
  },
});
```

## 构建配置

### Vite配置 (vite.config.ts)
```typescript
import { defineConfig } from 'vite';
import react from '@vitejs/plugin-react-swc';
import { resolve } from 'path';

export default defineConfig({
  plugins: [react()],
  resolve: {
    alias: {
      '@': resolve(__dirname, 'src'),
      '@components': resolve(__dirname, 'src/components'),
      '@pages': resolve(__dirname, 'src/pages'),
      '@services': resolve(__dirname, 'src/services'),
      '@themes': resolve(__dirname, 'src/themes'),
    },
  },
  server: {
    port: 5173,
    host: true,
    proxy: {
      '/api': {
        target: 'http://localhost:8000',
        changeOrigin: true,
        rewrite: (path) => path.replace(/^\/api/, ''),
      },
    },
  },
  build: {
    outDir: 'dist',
    sourcemap: true,
    rollupOptions: {
      output: {
        manualChunks: {
          vendor: ['react', 'react-dom'],
          mui: ['@mui/material', '@emotion/react', '@emotion/styled'],
        },
      },
    },
  },
});
```

### TypeScript配置 (tsconfig.json)
```json
{
  "compilerOptions": {
    "target": "ES2020",
    "useDefineForClassFields": true,
    "lib": ["ES2020", "DOM", "DOM.Iterable"],
    "module": "ESNext",
    "skipLibCheck": true,
    "moduleResolution": "bundler",
    "allowImportingTsExtensions": true,
    "resolveJsonModule": true,
    "isolatedModules": true,
    "noEmit": true,
    "jsx": "react-jsx",
    "strict": true,
    "noUnusedLocals": true,
    "noUnusedParameters": true,
    "noFallthroughCasesInSwitch": true,
    "baseUrl": ".",
    "paths": {
      "@/*": ["src/*"],
      "@components/*": ["src/components/*"],
      "@pages/*": ["src/pages/*"],
      "@services/*": ["src/services/*"],
      "@themes/*": ["src/themes/*"]
    }
  },
  "include": ["src"],
  "references": [{ "path": "./tsconfig.node.json" }]
}
```

## 性能优化

### 代码分割
```typescript
// 路由级别的代码分割
const ChatPage = lazy(() => import('../pages/chat'));
const JoinPage = lazy(() => import('../pages/join'));
const SetupPage = lazy(() => import('../pages/setup'));

// 组件级别的代码分割
const HeavyComponent = lazy(() => import('../components/HeavyComponent'));
```

### 虚拟滚动
```typescript
// 长列表优化
import { FixedSizeList as List } from 'react-window';

export const VirtualizedMessageList: React.FC<{ messages: Message[] }> = ({ messages }) => {
  const Row = ({ index, style }: { index: number; style: React.CSSProperties }) => (
    <div style={style}>
      <MessageItem message={messages[index]} />
    </div>
  );

  return (
    <List
      height={400}
      itemCount={messages.length}
      itemSize={80}
      width="100%"
    >
      {Row}
    </List>
  );
};
```

### 缓存策略
```typescript
// React Query用于数据缓存
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';

export const useClusterInfo = () => {
  return useQuery({
    queryKey: ['clusterInfo'],
    queryFn: () => clusterApi.getClusterInfo(),
    staleTime: 5 * 60 * 1000, // 5分钟
    refetchInterval: 30 * 1000, // 30秒自动刷新
  });
};
```

## 测试策略

### 推荐测试框架
- **单元测试**: Jest + React Testing Library
- **组件测试**: @testing-library/react
- **E2E测试**: Playwright 或 Cypress

### 测试示例
```typescript
// 组件测试示例
import { render, screen, fireEvent } from '@testing-library/react';
import { ChatInput } from '../chat-input';

describe('ChatInput', () => {
  test('sends message on form submit', async () => {
    const mockSendMessage = jest.fn();
    render(<ChatInput onSendMessage={mockSendMessage} />);

    const input = screen.getByPlaceholderText('输入消息...');
    const button = screen.getByRole('button');

    fireEvent.change(input, { target: { value: 'Hello' } });
    fireEvent.click(button);

    expect(mockSendMessage).toHaveBeenCalledWith('Hello');
    expect(input).toHaveValue('');
  });
});
```

## 部署配置

### 构建命令
```bash
# 开发环境构建
pnpm build

# 生产环境构建 (带分析)
pnpm build -- --analyze

# 预览构建结果
pnpm preview
```

### 环境变量
```bash
# .env.production
VITE_API_BASE_URL=https://api.parallax.ai
VITE_APP_NAME=Parallax
VITE_APP_VERSION=0.1.0
```

## 常见问题 (FAQ)

### Q: 如何添加新的页面？
A: 在 `src/pages/` 创建新组件，在 `src/router/index.tsx` 中添加路由配置。

### Q: 如何自定义主题？
A: 修改 `src/themes/` 目录下的配置文件，调整调色板、字体和组件样式。

### Q: 如何处理API错误？
A: 使用HTTP客户端的拦截器统一处理错误，或使用React Error Boundary捕获组件错误。

### Q: 如何优化首屏加载速度？
A: 使用代码分割、懒加载、资源预加载和缓存策略。

## 相关文件清单

### 核心文件
- `package.json` - 项目配置和依赖
- `tsconfig.json` - TypeScript配置
- `vite.config.ts` - Vite构建配置
- `src/App.tsx` - 应用根组件
- `src/main.tsx` - 应用入口

### 组件文件
- `src/components/` - 可复用组件库
- `src/pages/` - 页面级组件
- `src/router/` - 路由配置
- `src/services/` - 业务服务层

### API和工具
- `src/apis/` - API接口封装
- `src/themes/` - 主题系统
- `src/hooks/` - 自定义React Hooks
- `eslint.config.js` - ESLint配置
- `vite-env.d.ts` - Vite类型定义

---

*本文档由 AI 自动生成和更新，最后更新时间: 2025-01-21*