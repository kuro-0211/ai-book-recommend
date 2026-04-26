-- AI Book Recommender 초기 스키마
-- Django는 자체 ORM으로 테이블을 만들지만, n8n / PHP가 동일하게 참조해야 하므로
-- 동일한 구조의 테이블을 미리 정의해둡니다 (Django migrate 시 IF NOT EXISTS 처럼 동작).

CREATE DATABASE IF NOT EXISTS bookrec
  DEFAULT CHARACTER SET utf8mb4
  DEFAULT COLLATE utf8mb4_unicode_ci;

USE bookrec;

-- 사용자가 입력한 키워드 / 기분 단위 추천 요청 기록
CREATE TABLE IF NOT EXISTS recommender_recommendation (
  id            BIGINT AUTO_INCREMENT PRIMARY KEY,
  keyword       VARCHAR(255) NOT NULL,
  raw_response  LONGTEXT     NULL,
  created_at    DATETIME(6)  NOT NULL,
  KEY idx_keyword (keyword),
  KEY idx_created_at (created_at)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- 추천 응답을 책 단위로 정규화한 결과 (1 recommendation : N books)
CREATE TABLE IF NOT EXISTS recommender_book (
  id                BIGINT AUTO_INCREMENT PRIMARY KEY,
  recommendation_id BIGINT       NOT NULL,
  title             VARCHAR(500) NOT NULL,
  author            VARCHAR(255) NULL,
  summary           TEXT         NULL,
  reason            TEXT         NULL,
  position          INT          NOT NULL DEFAULT 0,
  created_at        DATETIME(6)  NOT NULL,
  KEY idx_recommendation (recommendation_id),
  CONSTRAINT fk_book_recommendation
    FOREIGN KEY (recommendation_id) REFERENCES recommender_recommendation(id)
    ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- n8n이 매주 월요일 오전 9시에 채우는 주간 TOP5 키워드 스냅샷
CREATE TABLE IF NOT EXISTS recommender_weeklytopkeyword (
  id          BIGINT AUTO_INCREMENT PRIMARY KEY,
  week_start  DATE         NOT NULL,
  rank_no     INT          NOT NULL,
  keyword     VARCHAR(255) NOT NULL,
  hit_count   INT          NOT NULL,
  created_at  DATETIME(6)  NOT NULL,
  UNIQUE KEY uniq_week_rank (week_start, rank_no)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
